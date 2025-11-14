#!/usr/bin/env python3
"""
Limpieza de archivos temporales con dry-run y reporte.
- Detecta *.tmp, *.temp, *.bak, *.old, *.log, *.cache, ~*, *.swp, *.swo
- También archivos .log/.cache/.tmp con mtime > --older-than días (por defecto 180)
- En --apply mueve a `99_Quarantine/Temp/` (no borra por defecto)
- Genera `temp_cleanup_report.json`

Uso:
  python3 cleanup_temp_files.py --dry-run
  python3 cleanup_temp_files.py --apply --older-than 90
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import shutil

BASE = Path(__file__).parent
QUARANTINE = BASE / "99_Quarantine" / "Temp"
REPORT_JSON = BASE / "temp_cleanup_report.json"

PATTERNS = [
    "*.tmp", "*.temp", "*.bak", "*.backup", "*.old",
    "~*", "*.swp", "*.swo", "*.log", "*.cache"
]

AGE_EXTS = {".log", ".cache", ".tmp"}


def is_candidate(path: Path, cutoff: datetime) -> bool:
    if not path.is_file():
        return False
    # nombre
    for pat in PATTERNS:
        if path.match(pat):
            return True
    # antiguos por extensión
    try:
        if path.suffix.lower() in AGE_EXTS:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < cutoff:
                return True
    except Exception:
        return False
    return False


def collect_candidates(root: Path, cutoff: datetime) -> list:
    items = []
    for p in root.rglob("*"):
        if p.is_file() and not p.name.startswith('.') and "99_Quarantine" not in p.parts:
            if is_candidate(p, cutoff):
                items.append(p)
    return items


def write_report(items: list):
    data = []
    for p in items:
        try:
            size = p.stat().st_size
            mtime = datetime.fromtimestamp(p.stat().st_mtime).isoformat()
        except Exception:
            size = None
            mtime = None
        data.append({
            "path": str(p),
            "size_bytes": size,
            "modified": mtime
        })
    REPORT_JSON.write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "count": len(items),
        "items": data
    }, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="No aplica cambios")
    ap.add_argument("--apply", action="store_true", help="Mueve archivos a cuarentena")
    ap.add_argument("--older-than", type=int, default=180, help="Días de antigüedad para .log/.cache/.tmp")
    args = ap.parse_args()

    cutoff = datetime.now() - timedelta(days=args.older_than)
    dry_run = args.dry_run and not args.apply

    print("🧹 Buscando archivos temporales...")
    items = collect_candidates(BASE, cutoff)
    print(f"Encontrados: {len(items)}")

    write_report(items)

    moved = 0
    if args.apply:
        print("🚚 Moviendo a cuarentena...")
        for p in items:
            rel = p.relative_to(BASE)
            dst = QUARANTINE / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(p), str(dst))
                moved += 1
            except Exception:
                continue

    print(f"✅ Listo. Candidatos: {len(items)} | Movidos: {moved} | Dry-run: {dry_run}")
    print(f"📄 Reporte: {REPORT_JSON}")

if __name__ == "__main__":
    main()



