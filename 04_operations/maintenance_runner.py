#!/usr/bin/env python3
"""
Orquestador de mantenimiento (dry-run por defecto).
- Lee organizer_config.json
- Ejecuta verify_organization.py, advanced_analyzer.py, deduplicate_files.py, cleanup_temp_files.py
- Genera índice HTML con enlaces a reportes y métricas resumidas

Uso:
  python3 maintenance_runner.py                # respeta config (dry-run por defecto)
  python3 maintenance_runner.py --apply-dedup  # aplica deduplicación (override)
  python3 maintenance_runner.py --apply-temp   # aplica limpieza temporales (override)
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
CONFIG = BASE / "organizer_config.json"
INDEX_HTML = BASE / "maintenance_index.html"


def run(cmd):
    try:
        result = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def generate_index(context):
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mantenimiento - Índice de Reportes</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; background:#f5f5f7; margin:0; padding:24px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    .card {{ background:#fff; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,.06); padding:20px; margin-bottom:16px; }}
    .title {{ font-size:22px; margin:0 0 8px; }}
    .muted {{ color:#666; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(260px,1fr)); gap:12px; }}
    a.btn {{ display:inline-block; background:#667eea; color:#fff; text-decoration:none; padding:8px 12px; border-radius:6px; margin-right:8px; }}
    .stat {{ font-size:20px; color:#667eea; font-weight:700; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1 class="title">Mantenimiento - Índice de Reportes</h1>
      <div class="muted">Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    </div>

    <div class="card">
      <div class="grid">
        <div>
          <div class="muted">Archivos totales</div>
          <div class="stat">{context.get('total_files','-')}</div>
        </div>
        <div>
          <div class="muted">Tasa de organización</div>
          <div class="stat">{context.get('organization_rate','-')}</div>
        </div>
        <div>
          <div class="muted">Grupos duplicados</div>
          <div class="stat">{context.get('duplicates_groups','-')}</div>
        </div>
        <div>
          <div class="muted">Temporales detectados</div>
          <div class="stat">{context.get('temp_candidates','-')}</div>
        </div>
        <div>
          <div class="muted">Archivos sueltos</div>
          <div class="stat">{context.get('loose_files','-')}</div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 class="title">Reportes</h2>
      <p>
        <a class="btn" href="organization_report.html">Verificación</a>
        <a class="btn" href="advanced_dashboard.html">Dashboard avanzado</a>
        <a class="btn" href="advanced_analysis.json">Análisis JSON</a>
        <a class="btn" href="duplicates_report.json">Duplicados JSON</a>
        <a class="btn" href="duplicates_report.csv">Duplicados CSV</a>
        <a class="btn" href="temp_cleanup_report.json">Temporales JSON</a>
        <a class="btn" href="large_files_report.json">Archivos grandes JSON</a>
        <a class="btn" href="large_files_report.csv">Archivos grandes CSV</a>
        <a class="btn" href="retention_report.json">Retención cuarentena</a>
      </p>
    </div>
  </div>
</body>
</html>
"""
    INDEX_HTML.write_text(html, encoding="utf-8")
    return INDEX_HTML


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}

    # 1) Verify organization (always dry-run here)
    rc, out, err = run(["python3", "verify_organization.py", "--dry-run"])
    # 2) Advanced analyzer
    if cfg.get("analyzer", {}).get("enabled", True):
        run(["python3", "advanced_analyzer.py"])  # genera dashboard y json
    
    # 3) Snapshot (dry-run para estimar)
    run(["python3", "snapshot_manager.py", "--dry-run"])

    # 4) Dedup (respect config unless overridden via CLI later)
    dedup_cmd = ["python3", "deduplicate_files.py"]
    if cfg.get("deduplicate", {}).get("dry_run", True):
        dedup_cmd.append("--dry-run")
    run(dedup_cmd)
    
    # 5) Temp cleanup
    temp_cmd = ["python3", "cleanup_temp_files.py"]
    if cfg.get("cleanup_temp", {}).get("dry_run", True):
        temp_cmd.append("--dry-run")
    older = str(cfg.get("cleanup_temp", {}).get("older_than_days", 180))
    temp_cmd.extend(["--older-than", older])
    run(temp_cmd)

    # 6) Large files report (50 MB por defecto)
    run(["python3", "large_files_report.py", "--min-mb", "50"])

    # 7) Retention report (dry-run 90 días)
    run(["python3", "retention_manager.py", "--dry-run", "--older-than", "90"])

    # Leer métricas rápidas
    context = {
        "total_files": "-",
        "organization_rate": "-",
        "duplicates_groups": "-",
        "temp_candidates": "-",
        "loose_files": "-"
    }
    try:
        adv_json = json.loads((BASE / "advanced_analysis.json").read_text(encoding="utf-8"))
        context["total_files"] = adv_json.get("metrics", {}).get("total_files", "-")
        rate = adv_json.get("metrics", {}).get("organization_rate", None)
        context["organization_rate"] = f"{rate:.1f}%" if isinstance(rate, (int, float)) else "-"
        context["duplicates_groups"] = len(adv_json.get("duplicates", []))
        context["temp_candidates"] = len(adv_json.get("temp_files", []))
    except Exception:
        pass

    try:
        org_json = json.loads((BASE / "organization_suggestions.json").read_text(encoding="utf-8"))
        # Si hay sugerencias, estimar sueltos
        loose = sum(len(v) for v in org_json.values())
        context["loose_files"] = loose
    except Exception:
        # En su defecto parsear HTML no trivial; dejamos "-"
        pass

    idx = generate_index(context)
    print(f"✅ Orquestación completada. Índice: {idx}")

if __name__ == "__main__":
    main()
