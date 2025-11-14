#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
AREAS = [
  '01_Marketing','02_Finance','03_Human_Resources','04_Business_Strategy','05_Technology',
  '06_Documentation','07_Advanced_Features','07_Risk_Management','08_AI_Artificial_Intelligence',
  '09_Sales','10_Customer_Service','11_Research_Development','11_System_Architecture',
  '12_Quality_Assurance','12_User_Guides','13_Legal_Compliance','13_Project_Status',
  '14_Procurement','14_Thought_Leadership','15_Logistics','16_Data_Analytics','17_Innovation',
  '18_Sustainability','19_International_Business','20_Project_Management'
]
EXTS = {'.pdf': 'pdf', '.pptx': 'pptx', '.xlsx': 'xlsx'}
EXCLUDE = {'.git','node_modules','__pycache__','backups','assets'}

moved = []

def fmt_size(n):
    for u in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}PB"

def area_for_path(rel: Path):
    return rel.parts[0] if rel.parts else 'root'

def main():
    assets_root = ROOT / 'assets'
    assets_root.mkdir(exist_ok=True)
    
    for root, dirs, files in os.walk(ROOT):
        # prune
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith('.')]
        for fn in files:
            if fn.startswith('.'): continue
            p = Path(root) / fn
            ext = p.suffix.lower()
            if ext not in EXTS: continue
            rel = p.relative_to(ROOT)
            # skip if already under assets/
            if rel.parts and rel.parts[0] == 'assets':
                continue
            area = area_for_path(rel)
            area = area if area in AREAS else 'misc'
            dest_dir = assets_root / area / EXTS[ext]
            dest_dir.mkdir(parents=True, exist_ok=True)
            target = dest_dir / p.name
            i = 1
            while target.exists():
                target = dest_dir / f"{p.stem}_{i}{p.suffix}"
                i += 1
            size = p.stat().st_size
            p.rename(target)
            moved.append((str(rel), str(target.relative_to(ROOT)), size))
    
    # Reporte
    report = ROOT / '06_Documentation' / 'ASSETS_REPORT.md'
    lines = [
        '# Reporte de Activos Movidos', '',
        f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', '',
        f'Total movidos: {len(moved)}', ''
    ]
    # Top 50 por tamaño
    top = sorted(moved, key=lambda x: -x[2])[:50]
    if top:
        lines.append('## Top 50 por tamaño')
        for src, dst, size in top:
            lines.append(f'- {src} → {dst} — {fmt_size(size)}')
    # Resumen por área
    from collections import defaultdict
    areas = defaultdict(int)
    sizes = defaultdict(int)
    for _, dst, size in moved:
        parts = Path(dst).parts
        area = parts[1] if len(parts) > 2 else 'misc'
        areas[area] += 1
        sizes[area] += size
    lines.append('')
    lines.append('## Resumen por área')
    for a in sorted(areas.keys()):
        lines.append(f'- {a}: {areas[a]} archivos — {fmt_size(sizes[a])}')
    report.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Movidos: {len(moved)} | Reporte: {report}")

if __name__ == '__main__':
    main()
