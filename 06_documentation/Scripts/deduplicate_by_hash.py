#!/usr/bin/env python3
import csv, shutil, hashlib
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / '06_Documentation' / 'duplicate_files_report.csv'
BACKUPS = ROOT / 'backups' / 'duplicates'

BACKUPS.mkdir(parents=True, exist_ok=True)

# Choose canonical: oldest mtime, then shortest path
def choose_canonical(paths):
    candidates = []
    for p in paths:
        fp = ROOT / p
        try:
            stat = fp.stat()
            candidates.append((stat.st_mtime, len(p), p))
        except Exception:
            continue
    if not candidates:
        return None
    candidates.sort()  # oldest, shortest
    return candidates[0][2]

moved = []
skipped = []

def main():
    if not REPORT.exists():
        print('No existe duplicate_files_report.csv')
        return
    with REPORT.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                count = int(row['count'])
            except Exception:
                continue
            if count < 2:
                continue
            paths = [p.strip() for p in row['paths'].split('|')]
            canonical = choose_canonical(paths)
            if not canonical:
                continue
            for p in paths:
                if p == canonical:
                    continue
                src = ROOT / p
                if not src.exists():
                    continue
                target_dir = BACKUPS / row['sha256']
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / src.name
                i = 1
                while target.exists():
                    target = target_dir / f"{src.stem}_{i}{src.suffix}"
                    i += 1
                try:
                    shutil.move(str(src), str(target))
                    moved.append((p, str(target.relative_to(ROOT)), canonical))
                except Exception as e:
                    skipped.append((p, str(e)))
    # Write log
    log = ROOT / '06_Documentation' / 'DEDUP_MOVES_LOG.md'
    lines = []
    lines.append(f"# Deduplicación por hash\n\n")
    lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    lines.append(f"Total duplicados movidos: {len(moved)}\n\n")
    lines.append("## Movimientos\n")
    for src, dst, keep in moved[:1000]:
        lines.append(f"- {src} → {dst} (se mantiene: {keep})")
    if skipped:
        lines.append("\n## Omitidos\n")
        for s, err in skipped[:200]:
            lines.append(f"- {s} ({err})")
    log.write_text("\n".join(lines), encoding='utf-8')
    print(f"Movidos: {len(moved)} | Omitidos: {len(skipped)} | Log: {log}")

if __name__ == '__main__':
    main()
