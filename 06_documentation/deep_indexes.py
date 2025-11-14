#!/usr/bin/env python3
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'.git','node_modules','__pycache__','backups'}

def fmt_size(n):
    for u in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}PB"

def breadcrumb(rel: Path):
    parts = list(rel.parts)
    crumbs = []
    acc = Path('.')
    for i,p in enumerate(parts):
        acc = acc / p
        link = './' + '/'.join(parts[:i+1]) + ('/' if i < len(parts)-1 else '')
        crumbs.append(f"[{p}]({link})")
    return ' / '.join(crumbs) if crumbs else '/'

def index_dir(d: Path):
    rel = d.relative_to(ROOT)
    items = [e for e in d.iterdir() if not e.name.startswith('.')]
    dirs = sorted([e for e in items if e.is_dir() and e.name not in EXCLUDE], key=lambda x:x.name.lower())
    files = sorted([e for e in items if e.is_file()], key=lambda x:x.name.lower())

    idx = [f"# Índice - {rel if rel!=Path('.') else '/'}\n",
           f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
           f"Breadcrumbs: {breadcrumb(rel)}\n",
           f"\nResumen: {len(dirs)} carpetas, {len(files)} archivos\n"]

    if dirs:
        idx.append("\n## Carpetas\n")
        for sd in dirs:
            # count inside
            fc = sum(1 for _ in sd.glob('*') if _.is_file())
            idx.append(f"- [{sd.name}](./{sd.name}/) — {fc} archivos")
    if files:
        idx.append("\n## Archivos\n")
        for f in files:
            try:
                st = f.stat()
                idx.append(f"- [{f.name}](./{f.name}) — {fmt_size(st.st_size)}")
            except Exception:
                idx.append(f"- {f.name}")

    (d/ 'INDEX.md').write_text('\n'.join(idx), encoding='utf-8')


def main():
    for root, dirs, files in os.walk(ROOT):
        # prune
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith('.')]
        d = Path(root)
        try:
            index_dir(d)
        except Exception:
            pass
    print('OK: Índices profundos generados')

if __name__ == '__main__':
    main()
