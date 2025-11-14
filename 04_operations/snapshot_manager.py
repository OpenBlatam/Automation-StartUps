#!/usr/bin/env python3
"""
Gestor de snapshots (copias de seguridad rápidas) en ZIP.
- Crea snapshot timestamp en 98_Backups/snapshots/
- Excluye 99_Quarantine y 98_Backups
- Dry-run: solo muestra qué se incluiría

Uso:
  python3 snapshot_manager.py --dry-run
  python3 snapshot_manager.py --apply
"""

import argparse
import os
from datetime import datetime
from pathlib import Path
import zipfile

BASE = Path(__file__).parent
BACKUPS_DIR = BASE / "98_Backups" / "snapshots"

EXCLUDES = {"99_Quarantine", "98_Backups"}


def should_include(path: Path) -> bool:
    parts = set(path.parts)
    return not (parts & EXCLUDES)


def create_snapshot(dry_run: bool) -> Path:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = BACKUPS_DIR / f"snapshot_{stamp}.zip"

    if dry_run:
        count = 0
        total_bytes = 0
        for p in BASE.rglob("*"):
            if p.is_file() and should_include(p.relative_to(BASE)):
                count += 1
                try:
                    total_bytes += p.stat().st_size
                except Exception:
                    pass
        print(f"[DRY-RUN] Archivos a incluir: {count} | Tamaño aprox: {total_bytes/1024/1024:.1f} MB")
        return out

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in BASE.rglob("*"):
            if p.is_file() and should_include(p.relative_to(BASE)):
                z.write(p, arcname=str(p.relative_to(BASE)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    dry = args.dry_run and not args.apply
    if dry:
        create_snapshot(True)
        print("✅ Snapshot (dry-run) listo.")
    else:
        out = create_snapshot(False)
        print(f"✅ Snapshot creado: {out}")

if __name__ == "__main__":
    main()



