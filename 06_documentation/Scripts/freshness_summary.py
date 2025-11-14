#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: freshness_summary.py <sop_linter_report.json>")
        return 2
    report = Path(sys.argv[1]).resolve()
    data = json.loads(report.read_text(encoding="utf-8"))
    results = data.get("results", [])

    # Classify freshness from presence-only (hint); detailed logic can be added if dates provided
    rows = [
        "# Freshness Summary (hint-based)",
        "",
        "file | type | freshness_hint | dead_links",
        "--- | --- | --- | ---",
    ]
    for r in results[:300]:
        rows.append(
            f"{r['file']} | {r['type']} | {('ok' if r['freshness_hint_present'] else 'missing')} | {len(r['dead_links'])}"
        )

    out_dir = report.parent
    (out_dir / "freshness_summary.md").write_text("\n".join(rows), encoding="utf-8")
    print(json.dumps({"ok": True, "written": str(out_dir / 'freshness_summary.md')}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


