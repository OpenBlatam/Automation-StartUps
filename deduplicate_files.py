#!/usr/bin/env python3
"""
Deduplicación segura por hash MD5 con soporte de dry-run y cuarentena.
- Identifica grupos de archivos duplicados (mismo contenido)
- Mantiene 1 archivo (criterio: el más antiguo por mtime)
- Mueve el resto a `99_Quarantine/Duplicates/` preservando estructura relativa
- Genera reporte JSON y CSV

Uso:
  python3 deduplicate_files.py --dry-run        # no mueve, solo reporta
  python3 deduplicate_files.py --apply          # mueve duplicados a cuarentena

Salidas:
  duplicates_report.json
  duplicates_report.csv
  99_Quarantine/Duplicates/... (cuando --apply)
"""

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE = Path(__file__).parent
QUARANTINE = BASE / "99_Quarantine" / "Duplicates"
REPORT_JSON = BASE / "duplicates_report.json"
REPORT_CSV = BASE / "duplicates_report.csv"


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(root: Path) -> list:
    by_hash = defaultdict(list)
    for p in root.rglob("*"):
        if p.is_file() and not p.name.startswith('.') and "99_Quarantine" not in p.parts:
            try:
                by_hash[md5sum(p)].append(p)
            except Exception:
                continue
    groups = [files for files in by_hash.values() if len(files) > 1]
    return groups


def choose_primary(files: list) -> Path:
    # Mantener el más antiguo por mtime
    return sorted(files, key=lambda f: f.stat().st_mtime)[0]


def move_to_quarantine(file_path: Path, base: Path, dry_run: bool) -> Path:
    rel = file_path.relative_to(base)
    target = QUARANTINE / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if not dry_run:
        shutil.move(str(file_path), str(target))
    return target


def write_reports(groups: list):
    data = []
    for g in groups:
        try:
            size = g[0].stat().st_size
        except Exception:
            size = None
        data.append({
            "count": len(g),
            "size_bytes": size,
            "files": [str(p) for p in g]
        })
    REPORT_JSON.write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "groups": data
    }, indent=2), encoding="utf-8")

    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["group_index", "count", "size_bytes", "file_path"])
        for i, g in enumerate(groups):
            size = None
            try:
                size = g[0].stat().st_size
            except Exception:
                pass
            for p in g:
                w.writerow([i, len(g), size, str(p)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="No aplica cambios")
    parser.add_argument("--apply", action="store_true", help="Mueve duplicados a cuarentena")
    args = parser.parse_args()

    dry_run = args.dry_run and not args.apply

    print("🔎 Buscando duplicados...")
    groups = find_duplicates(BASE)
    print(f"Encontrados {len(groups)} grupos")

    actions = []
    for files in groups:
        primary = choose_primary(files)
        for f in files:
            if f == primary:
                continue
            target = QUARANTINE / f.relative_to(BASE)
            actions.append({
                "from": str(f),
                "to": str(target),
                "keep": str(primary)
            })

    # Reportes
    write_reports(groups)

    moved = 0
    if args.apply:
        print("🚚 Moviendo duplicados a cuarentena...")
        for act in actions:
            src = Path(act["from"]) 
            dst = Path(act["to"]) 
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dst))
                moved += 1
            except Exception:
                continue

    print(f"✅ Listo. Grupos: {len(groups)} | Movidos: {moved} | Dry-run: {dry_run}")
    print(f"📄 Reportes: {REPORT_JSON} | {REPORT_CSV}")

if __name__ == "__main__":
    main()



