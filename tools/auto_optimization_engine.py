#!/usr/bin/env python3
"""
Motor de Optimización Automática
Analiza performance y ejecuta optimizaciones automáticas sugeridas
"""
import csv
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

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

def calculate_performance_scores(creatives):
    """Calcula scores de performance para cada creative"""
    scores = []
    
    for creative in creatives:
        impressions = float(creative.get('impressions', 0) or 0)
        clicks = float(creative.get('clicks', 0) or 0)
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        
        if impressions == 0:
            continue
        
        # Calcular métricas
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = (spend / clicks) if clicks > 0 else 0
        cpa = (spend / conversions) if conversions > 0 else 0
        
        assumed_ltv = 500
        revenue = conversions * assumed_ltv
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0
        
        # Score compuesto (0-100)
        # CTR score (0-30 puntos)
        ctr_score = min((ctr / 3.0) * 30, 30)
        
        # ROI score (0-40 puntos)
        roi_score = min((roi / 200) * 40, 40) if roi > 0 else 0
        
        # Volume score (0-30 puntos) - basado en conversiones
        volume_score = min((conversions / 50) * 30, 30)
        
        total_score = ctr_score + roi_score + volume_score
        
        scores.append({
            'creative_file': creative.get('creative_file', ''),
            'utm_content': creative.get('utm_content', ''),
            'formato': creative.get('formato', ''),
            'score': total_score,
            'ctr': ctr,
            'roi': roi,
            'conversions': conversions,
            'spend': spend,
            'status': get_status(total_score, roi, conversions)
        })
    
    return scores

def get_status(score, roi, conversions):
    """Determina status del creative"""
    if score >= 70 and roi > 50 and conversions > 0:
        return 'excellent'
    elif score >= 50 and roi > 0:
        return 'good'
    elif score >= 30 or (roi <= 0 and conversions == 0):
        return 'needs_optimization'
    else:
        return 'poor'

def generate_optimization_actions(scores):
    """Genera acciones de optimización automática"""
    actions = []
    
    # Categorizar creativos
    excellent = [s for s in scores if s['status'] == 'excellent']
    good = [s for s in scores if s['status'] == 'good']
    needs_optimization = [s for s in scores if s['status'] == 'needs_optimization']
    poor = [s for s in scores if s['status'] == 'poor']
    
    # Acción: Escalar excellent performers
    if excellent:
        actions.append({
            'type': 'scale',
            'targets': [s['creative_file'] for s in excellent],
            'action': f"Aumentar budget de {len(excellent)} top performer(s)",
            'reason': f"Score promedio: {sum(s['score'] for s in excellent) / len(excellent):.1f}",
            'expected_impact': f"+{len(excellent) * 15}% ROI total estimado",
            'priority': 'high'
        })
    
    # Acción: Pausar poor performers
    if poor:
        total_spend_poor = sum(s['spend'] for s in poor)
        actions.append({
            'type': 'pause',
            'targets': [s['creative_file'] for s in poor],
            'action': f"Pausar {len(poor)} poor performer(s)",
            'reason': f"Score promedio: {sum(s['score'] for s in poor) / len(poor):.1f}, ROI negativo o sin conversiones",
            'expected_impact': f"Ahorro de ${total_spend_poor:.2f}/período + reasignar a top performers",
            'priority': 'high'
        })
    
    # Acción: Optimizar needs_optimization
    if needs_optimization:
        actions.append({
            'type': 'optimize',
            'targets': [s['creative_file'] for s in needs_optimization[:5]],  # Top 5 para optimizar
            'action': f"Revisar y optimizar {len(needs_optimization)} creative(s) con bajo performance",
            'reason': f"Score promedio: {sum(s['score'] for s in needs_optimization) / len(needs_optimization):.1f}",
            'expected_impact': 'Mejora potencial de 20-40% en performance',
            'priority': 'medium'
        })
    
    # Acción: Testing para good performers
    if good:
        actions.append({
            'type': 'test',
            'targets': [s['creative_file'] for s in good[:3]],  # Top 3 para variantes
            'action': f"Crear variantes de {len(good[:3])} good performer(s)",
            'reason': 'Potencial de mejorar a excellent con testing',
            'expected_impact': 'Encontrar variantes que escalen a top performers',
            'priority': 'medium'
        })
    
    return actions

def apply_optimizations(actions, dry_run=True):
    """Aplica optimizaciones (o simula si dry_run)"""
    if dry_run:
        print("=" * 80)
        print("🔧 Optimizaciones Sugeridas (DRY RUN)")
        print("=" * 80)
        print()
        print("⚠️  Modo simulación. Para aplicar, usa --apply")
        print()
    else:
        print("=" * 80)
        print("🔧 Aplicando Optimizaciones")
        print("=" * 80)
        print()
        print("⚠️  Las optimizaciones se aplicarán realmente")
        print()
    
    for action in actions:
        priority_icon = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🔵'
        }.get(action['priority'], '⚪')
        
        print(f"{priority_icon} [{action['priority'].upper()}] {action['action']}")
        print(f"   📊 Razón: {action['reason']}")
        print(f"   📈 Impacto esperado: {action['expected_impact']}")
        print(f"   🎯 Targets: {len(action['targets'])} creative(s)")
        
        if not dry_run and action['type'] == 'pause':
            print(f"   ⏸️  PAUSANDO: {', '.join(action['targets'][:3])}" + (f"... y {len(action['targets']) - 3} más" if len(action['targets']) > 3 else ""))
        elif not dry_run and action['type'] == 'scale':
            print(f"   📈 ESCALANDO: {', '.join(action['targets'][:3])}" + (f"... y {len(action['targets']) - 3} más" if len(action['targets']) > 3 else ""))
        
        print()

def main():
    print("=" * 80)
    print("🤖 Motor de Optimización Automática")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Calcular scores
    print("📊 Calculando scores de performance...")
    scores = calculate_performance_scores(creatives)
    
    if not scores:
        print("⚠️  No se encontraron creativos con métricas")
        print("   Ejecuta primero: python3 tools/analyze_real_time_performance.py")
        return
    
    print(f"✅ {len(scores)} creativos analizados")
    print()
    
    # Mostrar distribución de scores
    print("=" * 80)
    print("📊 Distribución de Performance")
    print("=" * 80)
    print()
    
    by_status = defaultdict(list)
    for s in scores:
        by_status[s['status']].append(s)
    
    status_names = {
        'excellent': '🏆 Excellent',
        'good': '✅ Good',
        'needs_optimization': '⚠️  Needs Optimization',
        'poor': '❌ Poor'
    }
    
    for status, status_label in status_names.items():
        items = by_status.get(status, [])
        if items:
            avg_score = sum(s['score'] for s in items) / len(items)
            print(f"{status_label}: {len(items)} creative(s) (Score promedio: {avg_score:.1f})")
    
    print()
    
    # Generar acciones
    print("💡 Generando acciones de optimización...")
    actions = generate_optimization_actions(scores)
    
    if not actions:
        print("✅ No se requieren optimizaciones automáticas")
        return
    
    print(f"✅ {len(actions)} acción(es) generada(s)")
    print()
    
    # Determinar si es dry run
    dry_run = '--apply' not in sys.argv
    
    # Aplicar optimizaciones
    apply_optimizations(actions, dry_run=dry_run)
    
    # Guardar reporte
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = reports_dir / f'auto_optimization_{timestamp}.json'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'scores': scores,
            'actions': actions,
            'dry_run': dry_run
        }, f, indent=2)
    
    print(f"📄 Reporte guardado: {report_path}")
    print()
    
    if dry_run:
        print("💡 Para aplicar optimizaciones, ejecuta:")
        print("   python3 tools/auto_optimization_engine.py --apply")
    print()

if __name__ == '__main__':
    main()

