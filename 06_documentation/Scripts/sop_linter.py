#!/usr/bin/env python3
import re
import sys
import json
from pathlib import Path
from datetime import datetime


RE_MD_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


REQUIRED_SECTIONS_SOP = [
    "Procedimiento",  # pasos
    "Historial de cambios",
]

REQUIRED_SECTIONS_PROC = [
    "Objetivo",
    "Entradas",
    "RACI",
]


def find_md_links(text: str) -> list[str]:
    return RE_MD_LINK.findall(text)


def has_all_sections(text: str, sections: list[str]) -> bool:
    lower = text.lower()
    return all(section.lower() in lower for section in sections)


def classify_artifact(path: Path) -> str:
    name = path.name.lower()
    # SOP: solo nombres que empiezan con sop- o guías explícitas
    if name.startswith("sop-") or "guia_actualizacion_sops" in name:
        return "sop"
    # Proceso: solo nombres que empiezan con proc- o guías explícitas
    if name.startswith("proc-") or "guia_documentacion_procesos" in name:
        return "process"
    if "auditoria" in name:
        return "audit"
    if "onboarding" in name or "training" in name:
        return "training"
    if "template" in name or "templates" in name:
        return "template"
    return "other"


def validate_file(path: Path, root: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    artifact_type = classify_artifact(path)

    sections_ok = True
    if artifact_type == "sop":
        sections_ok = has_all_sections(text, REQUIRED_SECTIONS_SOP)
    elif artifact_type == "process":
        sections_ok = has_all_sections(text, REQUIRED_SECTIONS_PROC)

    links = find_md_links(text)
    dead_links: list[str] = []
    for href in links:
        if href.startswith("http://") or href.startswith("https://"):
            # skip external
            continue
        # normalize relative
        target = (path.parent / href).resolve()
        if not str(target).startswith(str(root.resolve())):
            # keep within repo; still allow but flag
            dead_links.append(href)
            continue
        if not target.exists():
            dead_links.append(href)

    freshness_hint_present = ("Última actualización:" in text) or ("Ultima actualizacion:" in text) or ("last_review" in text) or ("next_review" in text)

    return {
        "file": str(path.relative_to(root)),
        "type": artifact_type,
        "sections_ok": sections_ok,
        "dead_links": dead_links,
        "freshness_hint_present": freshness_hint_present,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: sop_linter.py <sgci_root_dir>")
        return 2

    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.exists():
        print(f"Directory not found: {root}")
        return 2

    results: list[dict] = []
    for path in root.rglob("*.md"):
        results.append(validate_file(path, root))

    summary = {
        "scanned": len(results),
        "sop_missing_sections": sum(1 for r in results if r["type"] == "sop" and not r["sections_ok"]),
        "proc_missing_sections": sum(1 for r in results if r["type"] == "process" and not r["sections_ok"]),
        "files_with_dead_links": sum(1 for r in results if r["dead_links"]),
        "missing_freshness_hint": sum(1 for r in results if not r["freshness_hint_present"]),
    }

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    report_dir = Path(__file__).parent.parent / "Reports_analytics"
    report_dir.mkdir(parents=True, exist_ok=True)

    # JSON report
    json_path = report_dir / "sop_linter_report.json"
    json_payload = {"timestamp": timestamp, "summary": summary, "results": results}
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown summary
    md_lines = [
        f"# SOP Linter Report ({timestamp})",
        "",
        "## Summary",
        f"- scanned: {summary['scanned']}",
        f"- sop_missing_sections: {summary['sop_missing_sections']}",
        f"- proc_missing_sections: {summary['proc_missing_sections']}",
        f"- files_with_dead_links: {summary['files_with_dead_links']}",
        f"- missing_freshness_hint: {summary['missing_freshness_hint']}",
        "",
        "## Findings",
        "file | type | sections_ok | dead_links | freshness_hint",
        "--- | --- | --- | --- | ---",
    ]
    for r in results:
        md_lines.append(
            f"{r['file']} | {r['type']} | {str(r['sections_ok']).lower()} | {len(r['dead_links'])} | {str(r['freshness_hint_present']).lower()}"
        )
    (report_dir / "sop_linter_report.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps({"ok": True, "summary": summary, "report_json": str(json_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



