#!/usr/bin/env python3
"""
Normalizador de nombres (kebab-case) con dry-run y manejo de colisiones.
- Convierte nombres a minúsculas, sin acentos, espacios->-, no alfanum -> -
- Compacta guiones múltiples, recorta guiones extremos
- Evita colisiones: añade sufijos -1, -2 ... si ya existe
- Dry-run por defecto: no renombra, solo reporta
- Genera mapping: rename_mapping.json

Uso:
  python3 normalize_names.py --dry-run
  python3 normalize_names.py --apply
"""

import argparse
import json
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).parent
REPORT = BASE / "rename_mapping.json"
EXCLUDES = {"99_Quarantine", "98_Backups", ".git", ".venv"}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDES)


def slugify(name: str) -> str:
    # separar extensión si es archivo
    if "." in name and not name.startswith('.'):
        base, ext = name.rsplit('.', 1)
        ext = '.' + ext
    else:
        base, ext = name, ''
    # normalizar
    base = unicodedata.normalize('NFKD', base)
    base = ''.join(ch for ch in base if not unicodedata.combining(ch))
    base = base.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base)
    base = re.sub(r"-+", "-", base).strip('-')
    if not base:
        base = "unnamed"
    return base + ext.lower()


def plan_renames(root: Path):
    plans = []
    # recorrer profundidad para renombrar archivos primero, luego carpetas de mayor profundidad
    all_paths = sorted([p for p in root.rglob("*") if not should_skip(p.relative_to(root))], key=lambda p: (p.is_dir(), len(p.parts)))
    existing = {p.relative_to(root): p for p in all_paths}

    for p in all_paths:
        rel = p.relative_to(root)
        parent = rel.parent
        new_name = slugify(rel.name)
        if new_name == rel.name:
            continue
        # resolver colisiones en el mismo directorio
        candidate = parent / new_name
        suffix = 1
        while candidate in existing or (root / candidate).exists():
            stem, dot, ext = new_name.partition('.')
            candidate = parent / f"{stem}-{suffix}{('.' + ext) if dot else ''}"
            suffix += 1
        plans.append({
            "type": "dir" if p.is_dir() else "file",
            "from": str(rel),
            "to": str(candidate)
        })
        # actualizar mapa existente para siguientes iteraciones
        existing.pop(rel, None)
        existing[candidate] = root / candidate
    return plans


def apply_renames(root: Path, plans):
    moved = 0
    # renombrar archivos primero, luego carpetas en orden inverso de profundidad
    files = [pl for pl in plans if pl["type"] == "file"]
    dirs = sorted([pl for pl in plans if pl["type"] == "dir"], key=lambda x: len(Path(x["from"]).parts), reverse=True)
    for batch in (files, dirs):
        for pl in batch:
            src = root / pl["from"]
            dst = root / pl["to"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                src.rename(dst)
                moved += 1
            except Exception:
                continue
    return moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run and not args.apply

    plans = plan_renames(BASE)
    REPORT.write_text(json.dumps({"planned": plans}, indent=2, ensure_ascii=False), encoding="utf-8")

    moved = 0
    if not dry and plans:
        moved = apply_renames(BASE, plans)
    print(f"✅ Normalización: planeados={len(plans)} | aplicados={moved} | dry-run={dry}")
    print(f"📄 Mapeo: {REPORT}")

if __name__ == "__main__":
    main()

