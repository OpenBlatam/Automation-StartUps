#!/usr/bin/env python3
"""
Generador Automático de Variantes de Creativos

Genera variantes automáticas de creativos exitosos con diferentes CTAs, formatos
o mensajes para testing y escalamiento.
"""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import random

CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'

# Templates de variantes
CTA_VARIANTS = [
    'Learn More',
    'Get Started',
    'Try Free',
    'Download Now',
    'Request Demo',
    'Book Meeting',
    'Sign Up',
    'Discover More',
    'View Details',
    'Start Trial'
]

ANGLE_VARIANTS = {
    'benefit': ['benefit', 'value_proposition', 'outcome'],
    'problem': ['problem', 'pain_point', 'challenge'],
    'social_proof': ['social_proof', 'testimonial', 'case_study'],
    'urgency': ['urgency', 'limited_time', 'exclusive'],
    'education': ['education', 'how_to', 'guide'],
    'entertainment': ['entertainment', 'story', 'narrative']
}

def load_csv() -> List[Dict]:
    """Carga el CSV Master"""
    if not CSV_MASTER.exists():
        print(f"❌ CSV Master no encontrado: {CSV_MASTER}")
        return []
    
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def identify_top_performers(creatives: List[Dict], top_n: int = 10) -> List[Dict]:
    """Identifica los creativos con mejor performance"""
    performers = []
    
    for c in creatives:
        ctr_val = c.get('ctr', '')
        if ctr_val:
            try:
                ctr = float(ctr_val.replace('%', ''))
                if ctr > 0.5:  # Solo considerar alto performance
                    performers.append((c, ctr))
            except:
                pass
    
    # Ordenar por CTR descendente
    performers.sort(key=lambda x: x[1], reverse=True)
    
    return [p[0] for p in performers[:top_n]]

def generate_variant(base: Dict, variant_type: str) -> Optional[Dict]:
    """Genera una variante de un creativo base"""
    variant = base.copy()
    
    if variant_type == 'cta':
        # Cambiar CTA
        new_cta = random.choice([cta for cta in CTA_VARIANTS if cta.lower() != base.get('cta', '').lower()])
        variant['cta'] = new_cta
        variant['utm_content'] = f"{base.get('utm_content', '')}_variant_cta_{new_cta.lower().replace(' ', '_')}"
    
    elif variant_type == 'angle':
        # Cambiar ángulo
        current_angle = base.get('angle', '').lower()
        if current_angle in ANGLE_VARIANTS:
            new_angle = random.choice(ANGLE_VARIANTS[current_angle])
            variant['angle'] = new_angle
            variant['utm_content'] = f"{base.get('utm_content', '')}_variant_angle_{new_angle}"
    
    elif variant_type == 'format':
        # Mantener mismo contenido pero sugerir cambio de formato
        variant['utm_content'] = f"{base.get('utm_content', '')}_variant_format"
        variant['suggested_format'] = 'carousel' if base.get('format', '').lower() != 'carousel' else 'single_image'
    
    # Marcar como variante
    variant['is_variant'] = 'true'
    variant['base_creative'] = base.get('utm_content', '')
    variant['variant_type'] = variant_type
    variant['generated_date'] = datetime.now().strftime('%Y-%m-%d')
    
    return variant

def generate_variants_report(creatives: List[Dict], variants: List[Dict], output_file: Path):
    """Genera reporte de variantes sugeridas"""
    report = f"""# 🎨 Variantes Generadas de Creativos

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Resumen

- **Creativos base analizados:** {len(creatives)}
- **Variantes generadas:** {len(variants)}
- **Variantes por tipo:**
  - CTA: {len([v for v in variants if v.get('variant_type') == 'cta'])}
  - Ángulo: {len([v for v in variants if v.get('variant_type') == 'angle'])}
  - Formato: {len([v for v in variants if v.get('variant_type') == 'format'])}

## 🎯 Variantes Sugeridas

"""
    
    # Agrupar por base creative
    by_base = {}
    for variant in variants:
        base = variant.get('base_creative', '')
        if base not in by_base:
            by_base[base] = []
        by_base[base].append(variant)
    
    for base_creative, base_variants in by_base.items():
        report += f"### Base: {base_creative}\n\n"
        
        for variant in base_variants:
            variant_type = variant.get('variant_type', '')
            report += f"- **Variante {variant_type}**: {variant.get('utm_content', '')}\n"
            
            if variant_type == 'cta':
                report += f"  - Nuevo CTA: {variant.get('cta', '')}\n")
            elif variant_type == 'angle':
                report += f"  - Nuevo ángulo: {variant.get('angle', '')}\n")
            elif variant_type == 'format':
                report += f"  - Formato sugerido: {variant.get('suggested_format', '')}\n")
            
            report += "\n"
    
    report += "\n## 💡 Recomendaciones\n\n"
    report += "1. **Implementar variantes** en campañas de A/B testing\n"
    report += "2. **Monitorear performance** de cada variante vs. original\n"
    report += "3. **Escalar** las variantes más exitosas\n"
    report += "4. **Iterar** basándose en resultados\n"
    
    output_file.write_text(report, encoding='utf-8')
    print(f"📄 Reporte guardado: {output_file}")

def save_variants_to_csv(variants: List[Dict], output_file: Path):
    """Guarda variantes en CSV"""
    if not variants:
        print("⚠️  No hay variantes para guardar")
        return
    
    # Leer CSV original para obtener headers
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
    
    if not fieldnames:
        print("❌ No se pudieron leer los headers del CSV")
        return
    
    # Añadir campos de variante si no existen
    variant_fields = ['is_variant', 'base_creative', 'variant_type', 'generated_date', 'suggested_format']
    for field in variant_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    
    # Guardar variantes
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(variants)
    
    print(f"💾 Variantes guardadas en CSV: {output_file}")

def main():
    print("=" * 80)
    print("🎨 Generador Automático de Variantes de Creativos")
    print("=" * 80)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
Uso: python3 tools/auto_generate_variants.py [opciones]

Opciones:
  --top-n N           Número de top performers a analizar (default: 10)
  --variants-per N    Variantes por creativo (default: 3)
  --types TYPE        Tipos de variantes: cta,angle,format o all (default: all)
  --output FILE       Archivo CSV de salida (default: exports/variants_TIMESTAMP.csv)
  --save-to-master    Guardar variantes directamente en CSV Master (requiere confirmación)
        """)
        return
    
    creatives = load_csv()
    
    if not creatives:
        return
    
    # Parse arguments
    top_n = 10
    variants_per = 3
    variant_types = ['cta', 'angle', 'format']
    output_file = None
    save_to_master = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--top-n':
            top_n = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--variants-per':
            variants_per = int(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--types':
            types_str = sys.argv[i+1]
            if types_str == 'all':
                variant_types = ['cta', 'angle', 'format']
            else:
                variant_types = types_str.split(',')
            i += 2
        elif sys.argv[i] == '--output':
            output_file = Path(sys.argv[i+1])
            i += 2
        elif sys.argv[i] == '--save-to-master':
            save_to_master = True
            i += 1
        else:
            i += 1
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    print(f"🔍 Identificando top {top_n} performers...")
    top_performers = identify_top_performers(creatives, top_n=top_n)
    
    if not top_performers:
        print("⚠️  No se encontraron creativos con CTR > 0.5%")
        print("   Considera usar --top-n con un valor mayor")
        return
    
    print(f"✅ Encontrados {len(top_performers)} creativos de alto performance")
    print()
    
    print("🎨 Generando variantes...")
    variants = []
    
    for base in top_performers:
        for _ in range(variants_per):
            variant_type = random.choice(variant_types)
            variant = generate_variant(base, variant_type)
            if variant:
                variants.append(variant)
    
    print(f"✅ Generadas {len(variants)} variantes")
    print()
    
    # Generar reporte
    reports_dir = Path(__file__).parent.parent / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = reports_dir / f'variants_report_{timestamp}.md'
    
    generate_variants_report(top_performers, variants, report_file)
    
    # Guardar en CSV
    if not output_file:
        output_file = Path(__file__).parent.parent / 'exports' / f'variants_{timestamp}.csv'
    
    save_variants_to_csv(variants, output_file)
    
    if save_to_master:
        confirm = input("\n⚠️  ¿Guardar variantes en CSV Master? (yes/no): ").strip().lower()
        if confirm == 'yes':
            # Añadir al final del CSV Master
            with open(CSV_MASTER, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=variants[0].keys())
                writer.writerows(variants)
            print(f"✅ Variantes añadidas a {CSV_MASTER}")
    
    # Resumen
    print()
    print("=" * 80)
    print("📊 Resumen")
    print("=" * 80)
    print(f"  🎯 Creativos base: {len(top_performers)}")
    print(f"  🎨 Variantes generadas: {len(variants)}")
    print(f"  📄 Reporte: {report_file}")
    print(f"  💾 CSV: {output_file}")
    print()

if __name__ == '__main__':
    main()

