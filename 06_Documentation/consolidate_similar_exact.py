#!/usr/bin/env python3
import csv, shutil, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / '06_Documentation' / 'duplicate_similar_report.csv'
BACK = ROOT / 'backups' / 'duplicates_similar'
LOG = ROOT / '06_Documentation' / 'SIMILAR_CONSOLIDATION_LOG.md'

BACK.mkdir(parents=True, exist_ok=True)

moves = []
errors = []

if not SRC.exists():
    print('No similar report found; aborting')
    raise SystemExit(0)

# Group candidates by directory when similarity==1.00 and same dir
from collections import defaultdict
candidates = defaultdict(list)
with SRC.open('r', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        try:
            sim = float(row['similarity'])
        except Exception:
            continue
        if sim != 1.0:
            continue
        p1 = Path(row['path1'])
        p2 = Path(row['path2'])
        if p1.parent != p2.parent:
            continue
        dirkey = str(p1.parent)
        candidates[dirkey].append((str(p1), str(p2)))

# For each pair, choose canonical (oldest mtime then shortest name), move the other to backup bucket by directory
seen = set()
for dirkey, pairs in candidates.items():
    for a, b in pairs:
        # avoid processing same file twice
        if (a,b) in seen or (b,a) in seen:
            continue
        seen.add((a,b))
        pa = ROOT / a
        pb = ROOT / b
        if not pa.exists() or not pb.exists():
            continue
        try:
            sa = pa.stat(); sb = pb.stat()
        except Exception:
            continue
        # canonical: oldest mtime, if tie shorter name
        keep, drop = (pa, pb)
        if sa.st_mtime > sb.st_mtime:
            keep, drop = (pb, pa)
        elif sa.st_mtime == sb.st_mtime and len(pa.name) > len(pb.name):
            keep, drop = (pb, pa)
        # move drop to backup under folder bucket
        bucket = BACK / dirkey.replace('/', '_')
        bucket.mkdir(parents=True, exist_ok=True)
        target = bucket / drop.name
        i = 1
        while target.exists():
            target = bucket / f"{drop.stem}_{i}{drop.suffix}"
            i += 1
        try:
            shutil.move(str(drop), str(target))
            moves.append((str(drop.relative_to(ROOT)), str(target.relative_to(ROOT)), str(keep.relative_to(ROOT))))
        except Exception as e:
            errors.append((str(drop.relative_to(ROOT)), str(e)))

# write log
lines = [
    '# Consolidación de duplicados por similitud 1.00 (misma carpeta)','','',
    f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}','',
    f'Total movidos: {len(moves)}',''
]
if moves:
    lines.append('## Movimientos (primeros 1000)')
    for src, dst, keep in moves[:1000]:
        lines.append(f'- {src} → {dst} (mantiene: {keep})')
if errors:
    lines.append('')
    lines.append('## Errores')
    for s, err in errors[:200]:
        lines.append(f'- {s} ({err})')
LOG.write_text('\n'.join(lines), encoding='utf-8')
print(f"Consolidated: {len(moves)} | Errors: {len(errors)} | Log: {LOG}")
