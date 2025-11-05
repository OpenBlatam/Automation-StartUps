#!/usr/bin/env python3
"""
Aplica movimientos sugeridos en organization_suggestions.json
"""

import json
import shutil
from pathlib import Path

BASE = Path(__file__).parent
SUGG = BASE / "organization_suggestions.json"


def main():
    if not SUGG.exists():
        print("No existe organization_suggestions.json. Ejecuta verify_organization.py primero.")
        return
    data = json.loads(SUGG.read_text(encoding="utf-8"))
    moved = 0
    skipped = 0
    for folder, suggestions in data.items():
        folder_path = Path(folder)
        # Asegurar rutas relativas a BASE si vienen absolutas
        if not folder_path.is_absolute():
            folder_path = BASE / folder_path
        for s in suggestions:
            src = folder_path / s["file"]
            dst = folder_path / s["move_to"]
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.exists():
                    if not dst.exists():
                        shutil.move(str(src), str(dst))
                        moved += 1
                    else:
                        skipped += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1
    print(f"✅ Movimientos aplicados: {moved}")
    print(f"⏭️  Omitidos: {skipped}")

if __name__ == "__main__":
    main()



