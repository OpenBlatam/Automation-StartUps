#!/usr/bin/env python3
"""
Etiquetador YAML para .md con dry-run y respaldo .bak.
- Si no tiene front matter, añade:
  ---\n title: <derivado del nombre>\n category: <carpeta principal>\n tags: [<subcarpeta(s)>]\n updated_at: <ISO8601>\n  ---
- Si ya tiene, solo actualiza updated_at (opcional)
- Dry-run: no modifica, genera previsualización en yaml_preview.json

Uso:
  python3 yaml_tagger.py --dry-run
  python3 yaml_tagger.py --apply
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
PREVIEW = BASE / "yaml_preview.json"
BACKUP_EXT = ".bak"

FRONT_MATTER_RE = re.compile(r"^---\n([\s\S]*?)\n---\n", re.M)


def derive_title(name: str) -> str:
    name = name.rsplit('.', 1)[0]
    name = name.replace('-', ' ').replace('_', ' ')
    return name.strip().title()


def first_dir_parts(rel: Path):
    parts = list(rel.parts)
    if len(parts) < 2:
        return (parts[0] if parts else '', [])
    return parts[0], parts[1:-1]


def build_front_matter(title: str, category: str, tags: list) -> str:
    tags_escaped = ', '.join([f"'{t}'" for t in tags if t])
    return (
        "---\n"
        f"title: '{title}'\n"
        f"category: '{category}'\n"
        f"tags: [{tags_escaped}]\n"
        f"updated_at: {datetime.now().isoformat()}\n"
        "---\n\n"
    )


def process_file(md_path: Path, dry: bool, previews: list):
    rel = md_path.relative_to(BASE)
    category, tag_parts = first_dir_parts(rel)
    title = derive_title(md_path.name)
    tags = [p for p in tag_parts if p]

    content = md_path.read_text(encoding='utf-8', errors='ignore')
    m = FRONT_MATTER_RE.match(content)
    if m:
        # actualizar updated_at al inicio del YAML
        yaml_block = m.group(1)
        if 'updated_at:' in yaml_block:
            yaml_block = re.sub(r"updated_at:\s*.*", f"updated_at: {datetime.now().isoformat()}", yaml_block)
        else:
            yaml_block += f"\nupdated_at: {datetime.now().isoformat()}"
        new_content = f"---\n{yaml_block}\n---\n" + content[m.end():]
        previews.append({"file": str(rel), "action": "update", "title": title, "category": category, "tags": tags})
        if not dry:
            (md_path.with_suffix(md_path.suffix + BACKUP_EXT)).write_text(content, encoding='utf-8')
            md_path.write_text(new_content, encoding='utf-8')
    else:
        fm = build_front_matter(title, category, tags)
        new_content = fm + content
        previews.append({"file": str(rel), "action": "insert", "title": title, "category": category, "tags": tags})
        if not dry:
            (md_path.with_suffix(md_path.suffix + BACKUP_EXT)).write_text(content, encoding='utf-8')
            md_path.write_text(new_content, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    dry = args.dry_run and not args.apply

    previews = []
    for md in BASE.rglob('*.md'):
        if any(part.startswith('.') for part in md.parts):
            continue
        process_file(md, dry, previews)

    PREVIEW.write_text(json.dumps({"preview": previews}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ Etiquetado YAML: archivos procesados={len(previews)} | dry-run={dry}")
    print(f"📄 Previsualización: {PREVIEW}")

if __name__ == '__main__':
    main()

