#!/usr/bin/env python3
"""
Quick Status Check
Muestra estado rápido del sistema en una sola línea
"""
import csv
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

def quick_check():
    """Ejecuta check rápido"""
    creatives = load_creatives()
    
    if not creatives:
        print("❌ CSV Master no encontrado")
        return
    
    total = len(creatives)
    
    # Contar con métricas
    with_metrics = sum(1 for c in creatives if float(c.get('impressions', 0) or 0) > 0)
    
    # Calcular totales
    total_impressions = sum(float(c.get('impressions', 0) or 0) for c in creatives)
    total_clicks = sum(float(c.get('clicks', 0) or 0) for c in creatives)
    total_spend = sum(float(c.get('spend', 0) or 0) for c in creatives)
    total_conversions = sum(float(c.get('conversions', 0) or 0) for c in creatives)
    
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    assumed_ltv = 500
    total_revenue = total_conversions * assumed_ltv
    total_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
    
    # Status icons
    roi_status = "✅" if total_roi > 50 else "⚠️" if total_roi > 0 else "❌"
    ctr_status = "✅" if avg_ctr > 2.0 else "⚠️" if avg_ctr > 1.0 else "❌"
    
    # Output compacto
    print(f"📊 Status: {total} creativos | {with_metrics} con métricas | "
          f"CTR: {ctr_status} {avg_ctr:.2f}% | ROI: {roi_status} {total_roi:.1f}% | "
          f"${total_spend:,.0f} gastado | {total_conversions:.0f} conversiones")

if __name__ == '__main__':
    quick_check()

