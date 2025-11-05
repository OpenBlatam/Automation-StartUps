#!/usr/bin/env python3
"""
Market Intelligence y Análisis Competitivo

Analiza el portfolio de creativos para identificar oportunidades de mercado,
tendencias emergentes y recomendaciones estratégicas basadas en data.
"""
import sys
import csv
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from datetime import datetime

CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'

# Benchmarks de industria
INDUSTRY_BENCHMARKS = {
    'linkedin': {
        'ctr': {'excellent': 0.8, 'good': 0.5, 'average': 0.3, 'poor': 0.1},
        'cvr': {'excellent': 15, 'good': 10, 'average': 5, 'poor': 2},
        'cpc': {'excellent': 2.0, 'good': 3.5, 'average': 5.0, 'poor': 8.0}
    }
}

def load_csv() -> List[Dict]:
    """Carga el CSV Master"""
    if not CSV_MASTER.exists():
        print(f"❌ CSV Master no encontrado: {CSV_MASTER}")
        return []
    
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def analyze_portfolio_gaps(creatives: List[Dict]) -> Dict:
    """Identifica gaps en el portfolio"""
    gaps = {
        'missing_formats': [],
        'missing_angles': [],
        'missing_products': [],
        'low_coverage': []
    }
    
    # Formate comunes en la industria
    industry_formats = ['carousel', 'single_image', 'video', 'document', 'text_ad']
    portfolio_formats = set(c.get('format', '').lower() for c in creatives if c.get('format'))
    
    gaps['missing_formats'] = [f for f in industry_formats if f not in portfolio_formats]
    
    # Ángulos comunes
    industry_angles = ['benefit', 'problem', 'social_proof', 'urgency', 'education', 'entertainment']
    portfolio_angles = set(c.get('angle', '').lower() for c in creatives if c.get('angle'))
    
    gaps['missing_angles'] = [a for a in industry_angles if a not in portfolio_angles]
    
    # Productos
    products = Counter(c.get('product', '') for c in creatives if c.get('product'))
    gaps['missing_products'] = [p for p, count in products.items() if count < 3]
    
    # Coverage bajo (pocos creativos por categoría)
    format_counts = Counter(c.get('format', '') for c in creatives if c.get('format'))
    gaps['low_coverage'] = [(f, count) for f, count in format_counts.items() if count < 2]
    
    return gaps

def analyze_market_opportunities(creatives: List[Dict]) -> Dict:
    """Identifica oportunidades de mercado"""
    opportunities = {
        'high_performing_gaps': [],
        'untested_combinations': [],
        'scaling_opportunities': [],
        'innovation_areas': []
    }
    
    # Encontrar combinaciones exitosas
    performance_by_combo = defaultdict(list)
    
    for c in creatives:
        format_val = c.get('format', '').lower()
        angle_val = c.get('angle', '').lower()
        ctr_val = c.get('ctr', '')
        
        if format_val and angle_val:
            combo = f"{format_val}+{angle_val}"
            
            try:
                ctr = float(ctr_val.replace('%', '')) if ctr_val else 0
                if ctr > 0.5:  # High performing
                    performance_by_combo[combo].append(ctr)
            except:
                pass
    
    # Identificar combinaciones que funcionan bien pero tienen pocas variantes
    for combo, ctrs in performance_by_combo.items():
        avg_ctr = sum(ctrs) / len(ctrs)
        count = len(ctrs)
        
        if avg_ctr > 0.8 and count < 3:
            opportunities['high_performing_gaps'].append({
                'combo': combo,
                'avg_ctr': f"{avg_ctr:.2f}%",
                'variants': count,
                'recommendation': f"Crear más variantes de {combo} (performance alta, pocas variantes)"
            })
    
    # Identificar áreas sin explorar
    formats = set(c.get('format', '').lower() for c in creatives if c.get('format'))
    angles = set(c.get('angle', '').lower() for c in creatives if c.get('angle'))
    
    for fmt in formats:
        for ang in angles:
            combo = f"{fmt}+{ang}"
            if combo not in performance_by_combo:
                opportunities['untested_combinations'].append(combo)
    
    # Scaling opportunities (performance alta, poco uso)
    high_performers = []
    for c in creatives:
        ctr_val = c.get('ctr', '')
        impressions = c.get('impressions', '')
        
        try:
            ctr = float(ctr_val.replace('%', '')) if ctr_val else 0
            imp = int(impressions) if impressions else 0
            
            if ctr > 0.8 and imp < 10000:  # High CTR but low reach
                high_performers.append({
                    'creative': c.get('utm_content', ''),
                    'ctr': f"{ctr:.2f}%",
                    'impressions': imp,
                    'recommendation': 'Aumentar budget para mayor alcance'
                })
        except:
            pass
    
    opportunities['scaling_opportunities'] = high_performers[:10]
    
    # Innovation areas (formats/angles nuevos no explorados)
    innovation_formats = ['interactive', 'ar', '360', 'story', 'live']
    innovation_angles = ['interactive', 'gamification', 'personalization']
    
    portfolio_formats = set(c.get('format', '').lower() for c in creatives if c.get('format'))
    portfolio_angles = set(c.get('angle', '').lower() for c in creatives if c.get('angle'))
    
    missing_innovations = {
        'formats': [f for f in innovation_formats if f not in portfolio_formats],
        'angles': [a for a in innovation_angles if a not in portfolio_angles]
    }
    
    opportunities['innovation_areas'] = missing_innovations
    
    return opportunities

def analyze_competitive_positioning(creatives: List[Dict]) -> Dict:
    """Analiza posicionamiento competitivo"""
    positioning = {
        'strengths': [],
        'weaknesses': [],
        'differentiators': [],
        'market_share_estimate': {}
    }
    
    # Analizar performance promedio vs. benchmarks
    ctrs = []
    cvrs = []
    
    for c in creatives:
        ctr_val = c.get('ctr', '')
        cvr_val = c.get('conversion_rate', '')
        
        try:
            if ctr_val:
                ctrs.append(float(ctr_val.replace('%', '')))
            if cvr_val:
                cvrs.append(float(cvr_val.replace('%', '')))
        except:
            pass
    
    if ctrs:
        avg_ctr = sum(ctrs) / len(ctrs)
        benchmarks = INDUSTRY_BENCHMARKS['linkedin']['ctr']
        
        if avg_ctr >= benchmarks['excellent']:
            positioning['strengths'].append(f"CTR excelente ({avg_ctr:.2f}% vs. benchmark {benchmarks['excellent']:.2f}%)")
        elif avg_ctr >= benchmarks['good']:
            positioning['strengths'].append(f"CTR bueno ({avg_ctr:.2f}%)")
        elif avg_ctr < benchmarks['poor']:
            positioning['weaknesses'].append(f"CTR bajo ({avg_ctr:.2f}% vs. benchmark promedio {benchmarks['average']:.2f}%)")
    
    if cvrs:
        avg_cvr = sum(cvrs) / len(cvrs)
        benchmarks = INDUSTRY_BENCHMARKS['linkedin']['cvr']
        
        if avg_cvr >= benchmarks['excellent']:
            positioning['strengths'].append(f"Tasa de conversión excelente ({avg_cvr:.2f}%)")
        elif avg_cvr < benchmarks['poor']:
            positioning['weaknesses'].append(f"Tasa de conversión baja ({avg_cvr:.2f}%)")
    
    # Identificar diferenciadores (combinaciones únicas)
    unique_combos = Counter()
    for c in creatives:
        format_val = c.get('format', '')
        angle_val = c.get('angle', '')
        product_val = c.get('product', '')
        
        if format_val and angle_val and product_val:
            combo = f"{format_val}|{angle_val}|{product_val}"
            unique_combos[combo] += 1
    
    # Comentarios únicos (aparecen pocas veces)
    for combo, count in unique_combos.items():
        if count == 1:
            parts = combo.split('|')
            positioning['differentiators'].append({
                'format': parts[0],
                'angle': parts[1],
                'product': parts[2],
                'note': 'Combinación única en portfolio'
            })
    
    # Estimación de market share (basada en diversidad)
    total_creatives = len(creatives)
    unique_formats = len(set(c.get('format', '') for c in creatives if c.get('format')))
    unique_angles = len(set(c.get('angle', '') for c in creatives if c.get('angle')))
    
    # Diversidad como proxy de market coverage
    diversity_score = (unique_formats * unique_angles) / max(total_creatives, 1)
    
    positioning['market_share_estimate'] = {
        'diversity_score': f"{diversity_score:.2f}",
        'coverage': 'Alta' if diversity_score > 0.5 else 'Media' if diversity_score > 0.2 else 'Baja',
        'total_creatives': total_creatives,
        'unique_formats': unique_formats,
        'unique_angles': unique_angles
    }
    
    return positioning

def generate_intelligence_report(gaps: Dict, opportunities: Dict, positioning: Dict, output_file: Path):
    """Genera reporte de market intelligence"""
    report = f"""# Market Intelligence Report

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Resumen Ejecutivo

Este reporte analiza el portfolio de creativos para identificar oportunidades de mercado, gaps estratégicos y recomendaciones de posicionamiento.

## 🔍 Gaps en el Portfolio

### Formatos Faltantes

"""
    
    if gaps['missing_formats']:
        for fmt in gaps['missing_formats']:
            report += f"- **{fmt}**: Oportunidad para diversificar\n"
    else:
        report += "*Todos los formatos principales están cubiertos*\n"
    
    report += "\n### Ángulos Faltantes\n\n"
    
    if gaps['missing_angles']:
        for angle in gaps['missing_angles']:
            report += f"- **{angle}**: Oportunidad para nuevos mensajes\n"
    else:
        report += "*Todos los ángulos principales están cubiertos*\n"
    
    report += "\n### Productos con Baja Cobertura\n\n"
    
    if gaps['missing_products']:
        for product in gaps['missing_products'][:5]:
            report += f"- **{product}**: Considerar más variantes\n"
    else:
        report += "*Buena cobertura de productos*\n"
    
    report += "\n## 💡 Oportunidades de Mercado\n\n"
    
    report += "### Combinaciones de Alto Performance con Pocas Variantes\n\n"
    if opportunities['high_performing_gaps']:
        for opp in opportunities['high_performing_gaps'][:5]:
            report += f"- **{opp['combo']}**: {opp['recommendation']}\n"
            report += f"  - CTR promedio: {opp['avg_ctr']}\n"
            report += f"  - Variantes actuales: {opp['variants']}\n\n"
    else:
        report += "*No hay gaps identificados*\n\n"
    
    report += "### Oportunidades de Escalamiento\n\n"
    if opportunities['scaling_opportunities']:
        for opp in opportunities['scaling_opportunities'][:5]:
            report += f"- **{opp['creative']}**: {opp['recommendation']}\n"
            report += f"  - CTR: {opp['ctr']}\n"
            report += f"  - Impresiones: {opp['impressions']:,}\n\n"
    else:
        report += "*No hay oportunidades de escalamiento identificadas*\n\n"
    
    report += "### Áreas de Innovación\n\n"
    innovation = opportunities['innovation_areas']
    if innovation['formats'] or innovation['angles']:
        report += "**Formatos nuevos:**\n"
        for fmt in innovation['formats']:
            report += f"- {fmt}\n"
        report += "\n**Ángulos nuevos:**\n"
        for angle in innovation['angles']:
            report += f"- {angle}\n"
    else:
        report += "*Portfolio está actualizado con formatos modernos*\n"
    
    report += "\n## 🎯 Posicionamiento Competitivo\n\n"
    
    report += "### Fortalezas\n\n"
    if positioning['strengths']:
        for strength in positioning['strengths']:
            report += f"- ✅ {strength}\n"
    else:
        report += "*No hay fortalezas claras identificadas*\n"
    
    report += "\n### Debilidades\n\n"
    if positioning['weaknesses']:
        for weakness in positioning['weaknesses']:
            report += f"- ⚠️  {weakness}\n"
    else:
        report += "*No hay debilidades críticas identificadas*\n"
    
    report += "\n### Diferenciadores\n\n"
    if positioning['differentiators']:
        for diff in positioning['differentiators'][:5]:
            report += f"- 🎨 **{diff['format']} + {diff['angle']} + {diff['product']}**: {diff['note']}\n"
    else:
        report += "*No hay diferenciadores únicos identificados*\n"
    
    report += "\n### Estimación de Market Coverage\n\n"
    mse = positioning['market_share_estimate']
    report += f"- **Diversidad Score:** {mse['diversity_score']}\n"
    report += f"- **Cobertura:** {mse['coverage']}\n"
    report += f"- **Total Creativos:** {mse['total_creatives']}\n"
    report += f"- **Formatos Únicos:** {mse['unique_formats']}\n"
    report += f"- **Ángulos Únicos:** {mse['unique_angles']}\n"
    
    report += "\n## 🚀 Recomendaciones Estratégicas\n\n"
    
    report += "1. **Priorizar gaps de alto performance**: Crear más variantes de combinaciones exitosas\n"
    report += "2. **Explorar áreas de innovación**: Probar formatos y ángulos nuevos\n"
    report += "3. **Escalar top performers**: Aumentar budget de creativos con alta CTR y bajo alcance\n"
    
    if gaps['missing_formats']:
        report += f"4. **Diversificar formatos**: Explorar {', '.join(gaps['missing_formats'][:3])}\n"
    
    if positioning['weaknesses']:
        report += "5. **Mejorar métricas débiles**: Enfocar en optimización de performance\n"
    
    output_file.write_text(report, encoding='utf-8')
    print(f"📄 Reporte guardado: {output_file}")

def main():
    print("=" * 80)
    print("🧠 Market Intelligence y Análisis Competitivo")
    print("=" * 80)
    print()
    
    creatives = load_csv()
    
    if not creatives:
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    print("🔍 Analizando gaps del portfolio...")
    gaps = analyze_portfolio_gaps(creatives)
    
    print("💡 Identificando oportunidades de mercado...")
    opportunities = analyze_market_opportunities(creatives)
    
    print("🎯 Analizando posicionamiento competitivo...")
    positioning = analyze_competitive_positioning(creatives)
    
    # Generar reporte
    reports_dir = Path(__file__).parent.parent / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = reports_dir / f'market_intelligence_{timestamp}.md'
    
    generate_intelligence_report(gaps, opportunities, positioning, output_file)
    
    # Resumen en consola
    print()
    print("=" * 80)
    print("📊 Resumen")
    print("=" * 80)
    print(f"  🔍 Gaps:")
    print(f"     - Formatos faltantes: {len(gaps['missing_formats'])}")
    print(f"     - Ángulos faltantes: {len(gaps['missing_angles'])}")
    print(f"  💡 Oportunidades:")
    print(f"     - Combinaciones de alto performance: {len(opportunities['high_performing_gaps'])}")
    print(f"     - Oportunidades de escalamiento: {len(opportunities['scaling_opportunities'])}")
    print(f"  🎯 Posicionamiento:")
    print(f"     - Fortalezas: {len(positioning['strengths'])}")
    print(f"     - Debilidades: {len(positioning['weaknesses'])}")
    print(f"     - Diferenciadores: {len(positioning['differentiators'])}")
    print()

if __name__ == '__main__':
    main()

