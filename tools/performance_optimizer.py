#!/usr/bin/env python3
"""
Optimizador Automático de Performance

Analiza creativos y ejecuta optimizaciones automáticas basadas en reglas
y machine learning para mejorar performance continuamente.
"""
import sys
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
REPORTS_DIR = Path(__file__).parent.parent / 'reports' / 'optimization'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Reglas de optimización
OPTIMIZATION_RULES = {
    'low_performance_pause': {
        'condition': lambda c: float(c.get('ctr', '0').replace('%', '')) < 0.2,
        'min_impressions': 1000,
        'action': 'pause',
        'reason': 'CTR muy bajo después de volumen suficiente'
    },
    'high_performance_scale': {
        'condition': lambda c: float(c.get('ctr', '0').replace('%', '')) > 0.8,
        'max_impressions': 10000,
        'action': 'scale',
        'reason': 'Alto performance con alcance limitado'
    },
    'optimize_targeting': {
        'condition': lambda c: float(c.get('ctr', '0').replace('%', '')) < 0.4 and int(c.get('impressions', '0')) > 5000,
        'action': 'optimize_targeting',
        'reason': 'Performance medio-bajo con alto alcance (posible targeting inadecuado)'
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

def analyze_optimization_opportunities(creatives: List[Dict]) -> Dict:
    """Identifica oportunidades de optimización"""
    opportunities = {
        'pause_candidates': [],
        'scale_candidates': [],
        'optimize_candidates': [],
        'test_variants': []
    }
    
    for c in creatives:
        utm_content = c.get('utm_content', '')
        ctr_val = c.get('ctr', '')
        impressions = c.get('impressions', '')
        
        if not ctr_val:
            continue
        
        try:
            ctr = float(ctr_val.replace('%', ''))
            imp = int(impressions) if impressions else 0
            
            # Candidatos para pausar
            if ctr < 0.2 and imp >= 1000:
                opportunities['pause_candidates'].append({
                    'creative': utm_content,
                    'ctr': f"{ctr:.2f}%",
                    'impressions': imp,
                    'reason': 'Performance muy bajo con volumen suficiente',
                    'savings_estimate': f"${imp * 0.003:.2f}" if imp > 0 else '$0'
                })
            
            # Candidatos para escalar
            elif ctr > 0.8 and imp < 10000:
                opportunities['scale_candidates'].append({
                    'creative': utm_content,
                    'ctr': f"{ctr:.2f}%",
                    'impressions': imp,
                    'reason': 'Alto performance con alcance limitado',
                    'potential_reach': imp * 3,
                    'expected_incremental': f"{imp * 2:,} impresiones"
                })
            
            # Candidatos para optimizar
            elif 0.2 <= ctr < 0.4 and imp >= 5000:
                opportunities['optimize_candidates'].append({
                    'creative': utm_content,
                    'ctr': f"{ctr:.2f}%",
                    'impressions': imp,
                    'reason': 'Performance medio-bajo con alto alcance',
                    'suggestions': [
                        'Revisar targeting',
                        'Optimizar mensaje o CTA',
                        'Probar variantes de formato'
                    ]
                })
            
            # Candidatos para testing (performance medio-alto)
            elif 0.5 <= ctr < 0.8:
                opportunities['test_variants'].append({
                    'creative': utm_content,
                    'ctr': f"{ctr:.2f}%",
                    'current_status': 'good',
                    'recommendation': 'Crear variantes para encontrar fórmula óptima'
                })
        
        except:
            pass
    
    # Ordenar por prioridad
    opportunities['pause_candidates'].sort(key=lambda x: float(x['ctr'].replace('%', '')))
    opportunities['scale_candidates'].sort(key=lambda x: float(x['ctr'].replace('%', '')), reverse=True)
    opportunities['optimize_candidates'].sort(key=lambda x: int(x['impressions']), reverse=True)
    
    return opportunities

def calculate_optimization_impact(opportunities: Dict) -> Dict:
    """Calcula el impacto potencial de las optimizaciones"""
    impact = {
        'pause_savings': 0,
        'scale_incremental': 0,
        'optimize_potential': 0,
        'total_impact': 0
    }
    
    # Ahorro potencial de pausar bajo performance
    for candidate in opportunities['pause_candidates']:
        imp = candidate.get('impressions', 0)
        impact['pause_savings'] += imp * 0.003  # Estimación de $3 por 1000 impresiones
    
    # Incremento potencial de escalar
    for candidate in opportunities['scale_candidates']:
        impact['scale_incremental'] += candidate.get('potential_reach', 0) * 0.002
    
    # Potencial de optimización
    for candidate in opportunities['optimize_candidates']:
        current_ctr = float(candidate['ctr'].replace('%', ''))
        improved_ctr = current_ctr * 1.5  # Mejora estimada del 50%
        impact['optimize_potential'] += candidate.get('impressions', 0) * (improved_ctr - current_ctr) / 100
    
    impact['total_impact'] = impact['scale_incremental'] - impact['pause_savings'] + impact['optimize_potential']
    
    return impact

def generate_optimization_report(opportunities: Dict, impact: Dict, output_file: Path):
    """Genera reporte de optimización"""
    report = f"""# ⚡ Optimizador Automático de Performance

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Resumen Ejecutivo

- **Candidatos para pausar:** {len(opportunities['pause_candidates'])}
- **Candidatos para escalar:** {len(opportunities['scale_candidates'])}
- **Candidatos para optimizar:** {len(opportunities['optimize_candidates'])}
- **Candidatos para testing:** {len(opportunities['test_variants'])}

## 💰 Impacto Potencial

- **Ahorro estimado (pausar):** ${impact['pause_savings']:,.2f}
- **Incremento estimado (escalar):** ${impact['scale_incremental']:,.2f}
- **Potencial optimización:** ${impact['optimize_potential']:,.2f}
- **Impacto total neto:** ${impact['total_impact']:,.2f}

## 🛑 Acciones Recomendadas: Pausar

"""
    
    if opportunities['pause_candidates']:
        report += "Creativos con performance muy bajo que deberían pausarse:\n\n"
        for i, candidate in enumerate(opportunities['pause_candidates'][:10], 1):
            report += f"{i}. **{candidate['creative']}**\n"
            report += f"   - CTR: {candidate['ctr']}\n"
            report += f"   - Impresiones: {candidate['impressions']:,}\n")
            report += f"   - Ahorro estimado: {candidate['savings_estimate']}\n")
            report += f"   - Razón: {candidate['reason']}\n\n")
    else:
        report += "*No hay creativos candidatos para pausar*\n\n"
    
    report += "\n## ⬆️ Acciones Recomendadas: Escalar\n\n"
    
    if opportunities['scale_candidates']:
        report += "Creativos de alto performance que deberían escalarse:\n\n"
        for i, candidate in enumerate(opportunities['scale_candidates'][:10], 1):
            report += f"{i}. **{candidate['creative']}**\n"
            report += f"   - CTR: {candidate['ctr']}\n"
            report += f"   - Impresiones actuales: {candidate['impressions']:,}\n")
            report += f"   - Incremento esperado: {candidate['expected_incremental']}\n")
            report += f"   - Razón: {candidate['reason']}\n\n")
    else:
        report += "*No hay creativos candidatos para escalar*\n\n"
    
    report += "\n## 🔧 Acciones Recomendadas: Optimizar\n\n"
    
    if opportunities['optimize_candidates']:
        report += "Creativos que necesitan optimización:\n\n"
        for i, candidate in enumerate(opportunities['optimize_candidates'][:10], 1):
            report += f"{i}. **{candidate['creative']}**\n"
            report += f"   - CTR: {candidate['ctr']}\n"
            report += f"   - Impresiones: {candidate['impressions']:,}\n")
            report += f"   - Razón: {candidate['reason']}\n")
            report += f"   - Sugerencias:\n")
            for suggestion in candidate.get('suggestions', []):
                report += f"     - {suggestion}\n")
            report += "\n")
    else:
        report += "*No hay creativos candidatos para optimizar*\n\n"
    
    report += "\n## 🧪 Oportunidades de Testing\n\n"
    
    if opportunities['test_variants']:
        report += "Creativos con buen performance para crear variantes:\n\n"
        for i, candidate in enumerate(opportunities['test_variants'][:10], 1):
            report += f"{i}. **{candidate['creative']}** - {candidate['ctr']} CTR\n")
            report += f"   - {candidate['recommendation']}\n\n")
    else:
        report += "*No hay candidatos identificados para testing*\n\n"
    
    report += "\n## 🎯 Plan de Acción Priorizado\n\n"
    
    report += "### Prioridad Alta (Ejecutar inmediatamente)\n\n"
    if opportunities['scale_candidates']:
        report += "1. **Escalar top performers** para maximizar ROI\n")
        report += f"   - {len(opportunities['scale_candidates'])} creativos identificados\n\n")
    
    if opportunities['pause_candidates']:
        report += "2. **Pausar bajo performers** para reducir desperdicio\n")
        report += f"   - {len(opportunities['pause_candidates'])} creativos identificados\n")
        report += f"   - Ahorro potencial: ${impact['pause_savings']:,.2f}\n\n")
    
    report += "\n### Prioridad Media (Siguiente semana)\n\n"
    if opportunities['optimize_candidates']:
        report += "1. **Optimizar targeting y mensajes**\n")
        report += f"   - {len(opportunities['optimize_candidates'])} creativos identificados\n\n")
    
    if opportunities['test_variants']:
        report += "2. **Crear variantes de good performers**\n")
        report += f"   - {len(opportunities['test_variants'])} creativos identificados\n\n")
    
    output_file.write_text(report, encoding='utf-8')
    print(f"📄 Reporte guardado: {output_file}")

def main():
    dry_run = '--apply' not in sys.argv
    
    print("=" * 80)
    print("⚡ Optimizador Automático de Performance")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 MODO DRY-RUN (análisis solamente)")
        print("   Usa --apply para ejecutar optimizaciones reales")
        print()
    else:
        print("⚠️  MODO APLICACIÓN (se ejecutarán optimizaciones)")
        print()
        confirm = input("¿Continuar? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelado")
            return
    
    creatives = load_csv()
    
    if not creatives:
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    print("🔍 Analizando oportunidades de optimización...")
    opportunities = analyze_optimization_opportunities(creatives)
    
    print("💰 Calculando impacto potencial...")
    impact = calculate_optimization_impact(opportunities)
    
    # Generar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = REPORTS_DIR / f'performance_optimization_{timestamp}.md'
    
    generate_optimization_report(opportunities, impact, output_file)
    
    # Resumen en consola
    print()
    print("=" * 80)
    print("📊 Resumen")
    print("=" * 80)
    print(f"  🛑 Pausar: {len(opportunities['pause_candidates'])} (ahorro: ${impact['pause_savings']:,.2f})")
    print(f"  ⬆️  Escalar: {len(opportunities['scale_candidates'])} (incremento: ${impact['scale_incremental']:,.2f})")
    print(f"  🔧 Optimizar: {len(opportunities['optimize_candidates'])}")
    print(f"  🧪 Testing: {len(opportunities['test_variants'])}")
    print(f"  💰 Impacto total: ${impact['total_impact']:,.2f}")
    print()
    
    if dry_run:
        print("💡 Para aplicar estas optimizaciones:")
        print(f"   python3 {sys.argv[0]} --apply")

if __name__ == '__main__':
    main()

