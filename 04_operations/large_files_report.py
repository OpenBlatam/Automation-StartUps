#!/usr/bin/env python3
"""
Reporte de archivos grandes.
- Escanea > --min-mb MB (por defecto 50 MB)
- Excluye 99_Quarantine y 98_Backups
- Genera large_files_report.json y large_files_report.csv

Uso:
  python3 large_files_report.py --min-mb 100
"""

import argparse
import json
import csv
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
JSON_OUT = BASE / "large_files_report.json"
CSV_OUT = BASE / "large_files_report.csv"
EXCLUDES = {"99_Quarantine", "98_Backups"}


def should_include(path: Path) -> bool:
    parts = set(path.parts)
    return not (parts & EXCLUDES)


def scan(min_mb: int) -> list:
    min_bytes = min_mb * 1024 * 1024
    items = []
    for p in BASE.rglob("*"):
        if p.is_file() and should_include(p.relative_to(BASE)):
            try:
                size = p.stat().st_size
            except Exception:
                continue
            if size >= min_bytes:
                items.append((p, size))
    items.sort(key=lambda x: x[1], reverse=True)
    return items


def write_reports(items: list):
    data = [
        {
            "path": str(p),
            "size_mb": size / 1024 / 1024
        }
        for p, size in items
    ]
    JSON_OUT.write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "count": len(items),
        "items": data
    }, indent=2), encoding="utf-8")

    with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "size_mb"])
        for p, size in items:
            w.writerow([str(p), f"{size/1024/1024:.2f}"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-mb", type=int, default=50)
    args = ap.parse_args()

    items = scan(args.min_mb)
    write_reports(items)
    print(f"✅ Archivos grandes: {len(items)} (>= {args.min_mb} MB)")
    print(f"📄 Reportes: {JSON_OUT} | {CSV_OUT}")

if __name__ == "__main__":
    main()



