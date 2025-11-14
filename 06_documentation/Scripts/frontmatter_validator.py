#!/usr/bin/env python3
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


YAML_FRONTMATTER_RE = re.compile(r"^---[\r\n]+([\s\S]*?)[\r\n]+---", re.MULTILINE)

REQUIRED_FIELDS = [
    "title",
    "artifact_type",
    "owner",
    "version",
]

DATE_FIELDS = ["last_review", "next_review"]


def parse_frontmatter(text: str) -> dict:
    m = YAML_FRONTMATTER_RE.search(text)
    if not m:
        return {}
    block = m.group(1)
    meta: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta


def validate_dates(meta: dict) -> list[str]:
    errs: list[str] = []
    def parse_date(s: str) -> Optional[datetime]:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d"):  # accept two formats
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
        return None
    last = parse_date(meta.get("last_review", "")) if meta.get("last_review") else None
    nxt = parse_date(meta.get("next_review", "")) if meta.get("next_review") else None
    if meta.get("last_review") and not last:
        errs.append("last_review con formato inválido")
    if meta.get("next_review") and not nxt:
        errs.append("next_review con formato inválido")
    if last and nxt and nxt <= last:
        errs.append("next_review debe ser posterior a last_review")
    return errs


def validate_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    fm = parse_frontmatter(text)
    missing = [f for f in REQUIRED_FIELDS if f not in fm]
    date_errs = validate_dates(fm)
    return {
        "file": str(path),
        "has_frontmatter": bool(fm),
        "missing_fields": missing,
        "date_errors": date_errs,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: frontmatter_validator.py <dir>")
        return 2
    root = Path(sys.argv[1]).resolve()
    results = []
    for p in root.rglob("*.md"):
        results.append(validate_file(p))
    summary = {
        "scanned": len(results),
        "missing_frontmatter": sum(1 for r in results if not r["has_frontmatter"]),
        "with_missing_fields": sum(1 for r in results if r["missing_fields"]),
        "with_date_errors": sum(1 for r in results if r["date_errors"]),
    }
    out_dir = root.parent / "Reports_analytics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "frontmatter_report.json").write_text(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Frontmatter Validation Report",
        "",
        "file | has_frontmatter | missing_fields | date_errors",
        "--- | --- | --- | ---",
    ]
    for r in results[:300]:
        lines.append(f"{Path(r['file']).name} | {str(r['has_frontmatter']).lower()} | {','.join(r['missing_fields'])} | {','.join(r['date_errors'])}")
    (out_dir / "frontmatter_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": True, "summary": summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


