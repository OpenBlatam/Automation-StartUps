#!/usr/bin/env python3
"""
Fijador de enlaces Markdown usando markdown_links_report.json.
- Para cada enlace roto, intenta reemplazar por la primera sugerencia válida
- Crea respaldo .bak por archivo
- Soporta --dry-run (no escribe)
- Reporta totales y lista breve de cambios por archivo

Uso:
  python3 link_fixer.py --dry-run
  python3 link_fixer.py --apply
"""

import argparse
import json
import re
from pathlib import Path

BASE = Path(__file__).parent
REPORT = BASE / "markdown_links_report.json"
BACKUP_EXT = ".bak"
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def load_issues():
    if not REPORT.exists():
        return []
    data = json.loads(REPORT.read_text(encoding='utf-8'))
    return data.get('issues', [])


def patch_file(md_path: Path, issues, dry: bool):
    text = md_path.read_text(encoding='utf-8', errors='ignore')
    original = text
    changed = False
    applied = []
    for issue in issues:
        old_url = issue['link']
        suggestions = issue.get('suggestions', [])
        if not suggestions:
            continue
        # Elegir la primera sugerencia
        new_rel = suggestions[0]
        try:
            new_url = str(Path(new_rel).relative_to(md_path.parent.relative_to(BASE)))
        except Exception:
            # si no se puede relativizar fácil, usar ruta sugerida tal cual
            new_url = new_rel
        # Reemplazar solo coincidencias exactas del link destino
        def repl(m):
            label, url = m.group(1), m.group(2)
            if url.strip() == old_url:
                nonlocal changed
                changed = True
                applied.append((old_url, new_url))
                return f"[{label}]({new_url})"
            return m.group(0)
        text = LINK_RE.sub(repl, text)
    if changed and not dry:
        (md_path.with_suffix(md_path.suffix + BACKUP_EXT)).write_text(original, encoding='utf-8')
        md_path.write_text(text, encoding='utf-8')
    return changed, applied


def group_issues_by_file(issues):
    grouped = {}
    for it in issues:
        f = it['file']
        grouped.setdefault(f, []).append(it)
    return grouped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    dry = args.dry_run and not args.apply

    issues = load_issues()
    grouped = group_issues_by_file(issues)

    total_files = 0
    total_links = 0
    changes_preview = []

    for rel, file_issues in grouped.items():
        md_path = BASE / rel
        if not md_path.exists():
            continue
        changed, applied = patch_file(md_path, file_issues, dry)
        if changed:
            total_files += 1
            total_links += len(applied)
            if applied:
                sample = applied[:5]
                changes_preview.append({
                    'file': rel,
                    'changes': sample,
                    'count': len(applied)
                })

    print(f"✅ Link fixer: archivos modificables={total_files}, enlaces corregibles={total_links}, dry-run={dry}")
    # Guardar preview
    (BASE / 'link_fixer_preview.json').write_text(
        json.dumps({'files': total_files, 'links': total_links, 'changes': changes_preview}, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print("📄 Preview: link_fixer_preview.json")

if __name__ == '__main__':
    main()

