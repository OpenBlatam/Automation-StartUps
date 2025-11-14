#!/usr/bin/env python3
import os, hashlib, csv, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / '06_Documentation'
REPORT = DOC_DIR / 'duplicate_files_report.csv'

EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__'}

# Pretty size
def fmt_size(n):
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

# Compute sha256
def file_hash(p: Path):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

# Generate index for a directory
def generate_index(dir_path: Path):
    items = []
    for entry in sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if entry.name.startswith('.'):
            continue
        if entry.is_dir():
            items.append((entry, True))
        else:
            items.append((entry, False))
    if not items:
        return
    idx_path = dir_path / 'INDEX.md'
    lines = []
    lines.append(f"# Índice - {dir_path.relative_to(ROOT)}\n")
    lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("\n## Carpetas\n")
    for entry, is_dir in items:
        if is_dir:
            lines.append(f"- [{entry.name}](./{entry.name}/)")
    lines.append("\n## Archivos\n")
    for entry, is_dir in items:
        if not is_dir:
            try:
                stat = entry.stat()
                size = fmt_size(stat.st_size)
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                lines.append(f"- [{entry.name}](./{entry.name}) — {size}, {mtime}")
            except Exception:
                lines.append(f"- {entry.name}")
    idx_path.write_text("\n".join(lines), encoding='utf-8')

# Walk tree to create indexes (top-level + first-level subdirs)
def create_all_indexes():
    targets = []
    for child in ROOT.iterdir():
        if child.name.startswith('.') or child.name in EXCLUDE_DIRS:
            continue
        if child.is_dir():
            targets.append(child)
            # also subdirs one level deep
            for sub in child.iterdir():
                if sub.is_dir() and not sub.name.startswith('.'):
                    targets.append(sub)
    for d in targets:
        try:
            generate_index(d)
        except Exception as e:
            print(f"WARN index {d}: {e}")

# Build duplicate report
def build_duplicate_report():
    hashes = {}
    for root, dirs, files in os.walk(ROOT):
        # prune
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for fn in files:
            if fn.startswith('.'):
                continue
            p = Path(root) / fn
            try:
                h = file_hash(p)
                size = p.stat().st_size
                hashes.setdefault((h, size), []).append(str(p.relative_to(ROOT)))
            except Exception:
                continue
    # write csv
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['sha256','size_bytes','count','paths'])
        for (h, size), paths in sorted(hashes.items(), key=lambda x: (-len(x[1]), x[0][1])):
            if len(paths) > 1:
                w.writerow([h, size, len(paths), ' | '.join(paths)])

if __name__ == '__main__':
    create_all_indexes()
    build_duplicate_report()
    print('OK: INDEX.md creados y duplicate_files_report.csv generado')
