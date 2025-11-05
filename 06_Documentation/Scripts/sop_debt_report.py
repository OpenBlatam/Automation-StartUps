#!/usr/bin/env python3
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


RE_CRIT = re.compile(r"criticality:\s*\"?(high|medium|low)\"?", re.IGNORECASE)
RE_NEXT = re.compile(r"next_review:\s*\"?([0-9]{4}-[0-9]{2}-[0-9]{2})\"?", re.IGNORECASE)


def parse_meta(text: str) -> Tuple[str, Optional[str]]:
    mcrit = RE_CRIT.search(text)
    crit = (mcrit.group(1).lower() if mcrit else "medium")
    mnext = RE_NEXT.search(text)
    next_rev = mnext.group(1) if mnext else None
    return crit, next_rev


def days_to(date_str: Optional[str]) -> Optional[int]:
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return int((dt - datetime.utcnow()).days)
    except Exception:
        return None


def priority(crit: str, days: Optional[int]) -> int:
    base = {"high": 100, "medium": 60, "low": 30}.get(crit, 50)
    if days is None:
        return base + 40  # sin fecha = urgente
    if days < 0:
        return base + 50  # vencido
    if days < 30:
        return base + 30
    if days < 60:
        return base + 15
    return base


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: sop_debt_report.py <sgci_root_dir>")
        return 2
    root = Path(sys.argv[1]).resolve()
    backlog = []
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        crit, next_rev = parse_meta(text)
        d = days_to(next_rev)
        score = priority(crit, d)
        backlog.append({
            "path": str(p.relative_to(root)),
            "criticality": crit,
            "next_review": next_rev,
            "days_to_next": d,
            "priority": score,
        })

    backlog.sort(key=lambda x: (-x["priority"], x["days_to_next"] if x["days_to_next"] is not None else 99999))

    out_dir = root.parent / "Reports_analytics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sop_debt_backlog.json").write_text(json.dumps(backlog, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Backlog de Deuda SOPs (priorizado)",
        "",
        "path | criticidad | next_review | días | prioridad",
        "--- | --- | --- | --- | ---",
    ]
    for it in backlog[:200]:
        lines.append(f"{it['path']} | {it['criticality']} | {it['next_review']} | {it['days_to_next']} | {it['priority']}")
    (out_dir / "sop_debt_backlog.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": True, "items": len(backlog)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



