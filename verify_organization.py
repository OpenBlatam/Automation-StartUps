#!/usr/bin/env python3
"""
Verificador de organización: detecta archivos fuera de subcarpetas esperadas
y genera un reporte HTML. Soporta --dry-run.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Carpetas a verificar
NUMERADAS = [
    "01_Marketing","02_Finance","03_Human_Resources","04_Business_Strategy","04_Operations",
    "05_Technology","06_Documentation","07_Risk_Management","08_AI_Artificial_Intelligence",
    "09_Sales","10_Customer_Service","13_Legal_Compliance","16_Data_Analytics","20_Project_Management",
]
TEMATICAS = ["ai_technology","VC_Venture_Capital","marketing"]

# Subcarpetas comunes esperadas (si existen en la carpeta padre)
COMMON_SUBFOLDERS = {
    "Guides","Templates","Scripts","Reports","Presentations","Data_Files","Checklists",
    "Analytics","Playbooks","User_Guides","Master_Documents","Index_Files","Troubleshooting",
    "Training_Materials","Reference_Docs","Other"
}

ALLOWED_ROOT_FILES = {"README.md", "readme.md", "index.md", "INDEX.md"}


def find_loose_files(dir_path: Path) -> List[Path]:
    """Devuelve archivos en el nivel raíz de dir_path (no ocultos)"""
    files = []
    for p in dir_path.iterdir():
        if p.is_file() and not p.name.startswith('.'):
            files.append(p)
    return files


def expected_subfolders(dir_path: Path) -> List[str]:
    return [d.name for d in dir_path.iterdir() if d.is_dir()]


def verify_folder(dir_path: Path) -> Dict:
    result = {
        "folder": str(dir_path),
        "loose_files": [],
        "suggestions": []
    }
    subfolders = set(expected_subfolders(dir_path))
    loose = find_loose_files(dir_path)
    for f in loose:
        if f.name in ALLOWED_ROOT_FILES:
            continue
        result["loose_files"].append(f.name)
        # Sugerencia simple por extensión
        ext = f.suffix.lower()
        suggestion = None
        if ext in {".py", ".js", ".ts"} and "Scripts" in subfolders:
            suggestion = f"Scripts/{f.name}"
        elif ext in {".ppt", ".pptx"} and "Presentations" in subfolders:
            suggestion = f"Presentations/{f.name}"
        elif ext in {".xlsx", ".xls", ".csv", ".json"} and "Data_Files" in subfolders:
            suggestion = f"Data_Files/{f.name}"
        elif ext in {".md", ".txt"} and ("Documentation" in subfolders or "Guides" in subfolders):
            target = "Documentation" if "Documentation" in subfolders else "Guides"
            suggestion = f"{target}/{f.name}"
        elif "Other" in subfolders:
            suggestion = f"Other/{f.name}"
        if suggestion:
            result["suggestions"].append({"file": f.name, "move_to": suggestion})
    return result


def generate_html_report(results: List[Dict], out_file: Path):
    total_loose = sum(len(r["loose_files"]) for r in results)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for r in results:
        if not r["loose_files"]:
            continue
        sugg_list = "".join(
            f"<li><code>{s['file']}</code> → <strong>{s['move_to']}</strong></li>"
            for s in r["suggestions"]
        )
        files_list = "".join(f"<li><code>{fn}</code></li>" for fn in r["loose_files"])
        rows.append(f"""
        <section>
          <h3>{r['folder']}</h3>
          <p><strong>Archivos sueltos:</strong> {len(r['loose_files'])}</p>
          <details open>
            <summary>Listado</summary>
            <ul>{files_list}</ul>
          </details>
          <details>
            <summary>Sugerencias</summary>
            <ul>{sugg_list}</ul>
          </details>
        </section>
        """)
    body = "\n".join(rows) if rows else "<p>Sin archivos sueltos. Todo OK ✅</p>"
    html = f"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Reporte Verificación Organización</title>
  <style>
    body {{ font-family: -apple-system, system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; }}
    code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 4px; }}
    section {{ border: 1px solid #eee; padding: 12px 16px; border-radius: 8px; margin: 12px 0; }}
    summary {{ cursor: pointer; }}
  </style>
</head>
<body>
  <h1>Reporte de Verificación de Organización</h1>
  <p>Fecha: {ts}</p>
  <p>Total de archivos sueltos: <strong>{total_loose}</strong></p>
  {body}
</body>
</html>
"""
    out_file.write_text(html, encoding="utf-8")


def main():
    base = Path(__file__).parent
    dry_run = ("--dry-run" in sys.argv) or ("-n" in sys.argv)

    targets = [*(base / n for n in NUMERADAS), *(base / n for n in TEMATICAS)]
    results: List[Dict] = []

    for d in targets:
        if not d.exists():
            continue
        results.append(verify_folder(d))

    report_path = base / "organization_report.html"
    generate_html_report(results, report_path)

    total_loose = sum(len(r["loose_files"]) for r in results)
    print(f"✅ Verificación completada. Archivos sueltos: {total_loose}")
    print(f"📄 Reporte: {report_path}")

    # Guardar JSON con sugerencias para automatizar futuro
    suggestions = {r["folder"]: r["suggestions"] for r in results if r["suggestions"]}
    (base / "organization_suggestions.json").write_text(
        json.dumps(suggestions, indent=2, ensure_ascii=False), encoding="utf-8"
    )

if __name__ == "__main__":
    main()



