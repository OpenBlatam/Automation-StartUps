#!/usr/bin/env python3
import os, json, chardet
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'.git','node_modules','__pycache__','backups'}
LOG = ROOT / '06_Documentation' / 'FRONTMATTER_LOG.md'

FRONTMATTER_OK = 0
FAILED = []

TAGS_BY_CAT = {
  '01_Marketing': ['marketing','business'],
  '05_Technology': ['technology','technical'],
  '02_Finance': ['finance','business'],
  '08_AI_Artificial_Intelligence': ['ai','artificial-intelligence']
}

def add_frontmatter(file_path: Path):
    global FRONTMATTER_OK
    raw = file_path.read_bytes()
    det = chardet.detect(raw)
    enc = det.get('encoding') or 'utf-8'
    try:
        text = raw.decode(enc, errors='strict')
    except Exception:
        # fallback latin-1
        try:
            text = raw.decode('latin-1')
        except Exception as e:
            FAILED.append((str(file_path.relative_to(ROOT)), f'decode_fail:{e}'))
            return
    if text.startswith('---'):
        return
    rel = file_path.relative_to(ROOT)
    parts = list(rel.parts)
    category = parts[0] if parts else 'General'
    tags = TAGS_BY_CAT.get(category, [])
    name = file_path.stem.replace('_',' ').title()
    fm = f"""---
title: "{name}"
category: "{category}"
tags: {json.dumps(tags)}
encoded_with: "{enc}"
created: "{datetime.now().strftime('%Y-%m-%d')}"
path: "{str(rel)}"
---

"""
    file_path.write_text(fm + text, encoding='utf-8')
    FRONTMATTER_OK += 1


def main():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith('.')]
        for fn in files:
            if fn.endswith('.md'):
                p = Path(root) / fn
                try:
                    add_frontmatter(p)
                except Exception as e:
                    FAILED.append((str(p.relative_to(ROOT)), str(e)))
    LOG.write_text(
        '# Frontmatter robusto\n\n'
        f'Añadidos: {FRONTMATTER_OK}\n\n'
        + ('## Fallos\n' + '\n'.join(f'- {p} ({err})' for p,err in FAILED) if FAILED else '')
        , encoding='utf-8')
    print(f'Frontmatter añadidos: {FRONTMATTER_OK} | Fallos: {len(FAILED)} | Log: {LOG}')

if __name__ == '__main__':
    main()
