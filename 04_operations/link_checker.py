#!/usr/bin/env python3
"""
Verificador de enlaces en Markdown (dry-run, reporte JSON).
- Busca [texto](ruta) en .md
- Verifica rutas relativas existentes dentro del repo
- Reporta rotos y sugiere alternativas cercanas por nombre (mismo directorio o índice)

Uso:
  python3 link_checker.py --dry-run
"""

import argparse
import json
import re
from pathlib import Path

BASE = Path(__file__).parent
REPORT = BASE / "markdown_links_report.json"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def collect_md_files():
    for p in BASE.rglob('*.md'):
        if any(part.startswith('.') for part in p.parts):
            continue
        yield p


def nearest_candidates(src_dir: Path, target_name: str):
    # Busca por nombre base en el mismo directorio y uno arriba
    name = Path(target_name).name.lower()
    cands = []
    for scope in [src_dir, src_dir.parent]:
        try:
            for p in scope.glob('**/*'):
                if p.is_file() and p.name.lower() == name:
                    cands.append(str(p.relative_to(BASE)))
        except Exception:
            continue
    return sorted(set(cands))[:5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    issues = []
    for md in collect_md_files():
        rel = md.relative_to(BASE)
        text = md.read_text(encoding='utf-8', errors='ignore')
        for m in LINK_RE.finditer(text):
            url = m.group(1).strip()
            if url.startswith('http://') or url.startswith('https://') or url.startswith('#'):
                continue
            # Normalizar relativos
            target = (md.parent / url).resolve()
            try:
                target_rel = target.relative_to(BASE.resolve())
            except Exception:
                target_rel = None
            if not target.exists():
                suggestions = nearest_candidates(md.parent, url)
                issues.append({
                    'file': str(rel), 'link': url,
                    'suggestions': suggestions
                })
    REPORT.write_text(json.dumps({'count': len(issues), 'issues': issues}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ QA enlaces: encontrados {len(issues)} rotos. Reporte: {REPORT}")

if __name__ == '__main__':
    main()

