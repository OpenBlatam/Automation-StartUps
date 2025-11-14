#!/usr/bin/env python3
"""
Gestor de retención para cuarentena.
- Enumera elementos en 99_Quarantine con antigüedad > --older-than días
- Dry-run: solo reporta
- Apply: elimina archivos candidatos (no vacía carpetas a menos que queden vacías)

Uso:
  python3 retention_manager.py --dry-run --older-than 30
  python3 retention_manager.py --apply --older-than 90
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import json

BASE = Path(__file__).parent
QUARANTINE = BASE / "99_Quarantine"
REPORT = BASE / "retention_report.json"


def collect_candidates(older_days: int):
    cutoff = datetime.now() - timedelta(days=older_days)
    items = []
    if not QUARANTINE.exists():
        return items
    for p in QUARANTINE.rglob("*"):
        if p.is_file():
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
            except Exception:
                continue
            if mtime < cutoff:
                items.append((p, mtime))
    return items


def write_report(items, older_days):
    data = [
        {
            "path": str(p),
            "modified": m.isoformat()
        }
        for p, m in items
    ]
    REPORT.write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "older_than_days": older_days,
        "count": len(items),
        "items": data
    }, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--older-than", type=int, default=90)
    args = ap.parse_args()

    dry = args.dry_run and not args.apply

    items = collect_candidates(args.older_than)
    write_report(items, args.older_than)

    removed = 0
    if not dry:
        for p, _ in items:
            try:
                p.unlink(missing_ok=True)
                removed += 1
            except Exception:
                continue
        # Intento opcional: limpiar carpetas vacías
        for d in sorted({p.parent for p, _ in items}, key=lambda x: len(str(x)), reverse=True):
            try:
                if d.exists() and not any(d.iterdir()):
                    d.rmdir()
            except Exception:
                pass

    print(f"✅ Retención: candidatos={len(items)} | eliminados={removed} | dry-run={dry}")
    print(f"📄 Reporte: {REPORT}")

if __name__ == "__main__":
    main()



