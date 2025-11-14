#!/usr/bin/env python3
import json
from pathlib import Path


def load_table_md(json_path: Path, fields: list[str], headers: list[str]) -> list[str]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    rows = [" | ".join(headers), " | ".join(["---"] * len(headers))]
    results = data.get("results", data if isinstance(data, list) else [])
    for r in results[:200]:
        rows.append(" | ".join(str(r.get(f, "")) for f in fields))
    return rows


def main():
    root = Path(__file__).parent.parent
    reports = root / "Reports_analytics"
    out = root / "00_Sistema_Gestion_Conocimiento_Interno/11_Dashboard_Metricas_KM_Generado.md"

    parts: list[str] = ["# 📊 Dashboard KM - Generado\n"]

    # Linter summary
    linter = reports / "sop_linter_report.json"
    if linter.exists():
        d = json.loads(linter.read_text(encoding="utf-8"))
        parts.append("## Resumen Linter\n")
        for k, v in d.get("summary", {}).items():
            parts.append(f"- {k}: {v}")
        parts.append("")

    # Freshness summary
    fresh = reports / "freshness_summary.md"
    if fresh.exists():
        parts.append("## Freshness\n")
        parts.append(fresh.read_text(encoding="utf-8"))
        parts.append("")

    # SOP debt backlog (top 50)
    debt = reports / "sop_debt_backlog.json"
    if debt.exists():
        d = json.loads(debt.read_text(encoding="utf-8"))
        parts.append("## Deuda SOPs (Top 50)\n")
        parts.append("path | criticidad | next_review | días | prioridad")
        parts.append("--- | --- | --- | --- | ---")
        for it in d[:50]:
            parts.append(f"{it['path']} | {it['criticality']} | {it['next_review']} | {it['days_to_next']} | {it['priority']}")
        parts.append("")

    out.write_text("\n".join(parts), encoding="utf-8")
    print(json.dumps({"ok": True, "written": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()


