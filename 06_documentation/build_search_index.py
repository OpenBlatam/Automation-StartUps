#!/usr/bin/env python3
"""
Construye un índice global de búsqueda (search_index.json).
- Escanea .md, .txt, .html, .pdf, .py, .js, .ts
- Extrae: path, size, mtime, title (YAML o derivado), tags (YAML), category (carpeta raíz)
- Limita contenido a snippet inicial (para vista previa) en texto plano cuando aplica
"""

import json
import re
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
OUT = BASE / "search_index.json"

FRONT_RE = re.compile(r"^---\n([\s\S]*?)\n---\n", re.M)
TITLE_RE = re.compile(r"^#\s+(.+)$", re.M)

INCLUDE_EXTS = {".md", ".txt", ".html", ".pdf", ".py", ".js", ".ts"}
TEXT_EXTS = {".md", ".txt", ".html", ".py", ".js", ".ts"}


def derive_title(path: Path, text: str) -> str:
    m = TITLE_RE.search(text) if text else None
    if m:
        return m.group(1).strip()
    return path.stem.replace('-', ' ').replace('_', ' ').title()


def parse_yaml(text: str):
    m = FRONT_RE.match(text or "")
    if not m:
        return {}, text
    yaml_block = m.group(1)
    body = text[m.end():]
    data = {}
    for line in yaml_block.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip()] = v.strip().strip("'\"")
    # tags list
    if 'tags' in data and data['tags'].startswith('[') and data['tags'].endswith(']'):
        items = [i.strip().strip("'\"") for i in data['tags'][1:-1].split(',') if i.strip()]
        data['tags'] = items
    return data, body


def main():
    entries = []
    for p in BASE.rglob('*'):
        if not p.is_file():
            continue
        if any(part.startswith('.') for part in p.parts):
            continue
        if p.suffix.lower() not in INCLUDE_EXTS:
            continue
        rel = p.relative_to(BASE)
        category = rel.parts[0] if len(rel.parts) else ''
        try:
            size = p.stat().st_size
            mtime = datetime.fromtimestamp(p.stat().st_mtime).isoformat()
        except Exception:
            size, mtime = None, None
        text = ''
        title = ''
        tags = []
        if p.suffix.lower() in TEXT_EXTS:
            try:
                raw = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                raw = ''
            meta, body = parse_yaml(raw)
            title = meta.get('title') or derive_title(p, raw)
            tags = meta.get('tags') or []
            snippet = (body or raw)[:800]
            entries.append({
                'path': str(rel), 'size': size, 'mtime': mtime,
                'title': title, 'tags': tags, 'category': category,
                'snippet': snippet
            })
        else:
            # Non-text placeholders (e.g., PDF)
            title = derive_title(p, '')
            entries.append({
                'path': str(rel), 'size': size, 'mtime': mtime,
                'title': title, 'tags': tags, 'category': category
            })
    OUT.write_text(json.dumps({'generated_at': datetime.now().isoformat(), 'count': len(entries), 'items': entries}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ Índice generado: {OUT} (items={len(entries)})")

if __name__ == '__main__':
    main()

