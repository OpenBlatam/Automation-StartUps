#!/usr/bin/env python3
"""
Mantenimiento: limpiar carpetas Other y generar índices README.md en subcarpetas.
"""

import os
import shutil
from pathlib import Path

MAIN_FOLDERS = [
    "01_Marketing","02_Finance","03_Human_Resources","04_Business_Strategy","04_Operations",
    "05_Technology","06_Documentation","07_Risk_Management","08_AI_Artificial_Intelligence",
    "09_Sales","10_Customer_Service","13_Legal_Compliance","16_Data_Analytics","20_Project_Management",
]
THEME_FOLDERS = ["ai_technology","VC_Venture_Capital","marketing"]

EXT_TO_FOLDER = {
    ".py": "Scripts",
    ".js": "Scripts",
    ".ts": "Scripts",
    ".ipynb": "Scripts",
    ".json": "Data_Files",
    ".csv": "Data_Files",
    ".xlsx": "Data_Files",
    ".xls": "Data_Files",
    ".pptx": "Presentations",
    ".ppt": "Presentations",
    ".docx": "Templates",
    ".doc": "Templates",
    ".html": "Templates",
    ".pdf": "Reports",
    ".md": "Documentation",
    ".txt": "Documentation",
}


def relink(target_dir: Path, dry_run: bool = False) -> int:
    moved = 0
    other = target_dir / "Other"
    if not other.exists() or not other.is_dir():
        return 0
    # build available targets in dir
    existing = {p.name for p in target_dir.iterdir() if p.is_dir()}
    for item in other.iterdir():
        if item.is_dir():
            continue
        ext = item.suffix.lower()
        dest_name = EXT_TO_FOLDER.get(ext)
        if dest_name and dest_name in existing:
            dest = target_dir / dest_name / item.name
            if not dry_run:
                try:
                    if not dest.exists():
                        shutil.move(str(item), str(dest))
                        moved += 1
                except Exception:
                    pass
    return moved


def write_readme(directory: Path) -> None:
    files = [p for p in directory.iterdir() if p.is_file() and not p.name.startswith('.') and p.name.lower() != "readme.md"]
    subdirs = [p for p in directory.iterdir() if p.is_dir()]
    lines = []
    lines.append(f"# {directory.name}\n\n")
    if subdirs:
        lines.append("## Subcarpetas\n")
        for d in sorted(subdirs, key=lambda x: x.name.lower()):
            lines.append(f"- {d.name}/\n")
        lines.append("\n")
    if files:
        lines.append("## Archivos\n")
        for f in sorted(files, key=lambda x: x.name.lower()):
            rel = f.name
            lines.append(f"- {rel}\n")
        lines.append("\n")
    readme = directory / "README.md"
    content = "".join(lines)
    try:
        with open(readme, "w", encoding="utf-8") as fh:
            fh.write(content)
    except Exception:
        pass


def generate_indices(base: Path) -> int:
    count = 0
    for root, dirs, _ in os.walk(base):
        # Solo a profundidad razonable
        if root.count(os.sep) - str(base).count(os.sep) > 3:
            continue
        dpath = Path(root)
        write_readme(dpath)
        count += 1
    return count


def main():
    base = Path(__file__).parent
    total_moved = 0
    # Limpieza de Other en principales y temáticas
    for name in MAIN_FOLDERS + THEME_FOLDERS:
        d = base / name
        if d.exists():
            total_moved += relink(d, dry_run=False)
    # Índices
    total_indices = 0
    for name in MAIN_FOLDERS + THEME_FOLDERS:
        d = base / name
        if d.exists():
            total_indices += generate_indices(d)
    print(f"✅ Limpieza completada. Movidos desde Other: {total_moved}")
    print(f"✅ README generados/actualizados: {total_indices}")

if __name__ == "__main__":
    main()



