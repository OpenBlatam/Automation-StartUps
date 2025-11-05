#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta


FM_TEMPLATE = """---
title: "{title}"
artifact_type: "{artifact_type}"
code: "{code}"
owner: "{owner}"
approver: "{approver}"
version: "1.0"
status: "active"
criticality: "{criticality}"
review_sla_months: {sla}
last_review: "{last_review}"
next_review: "{next_review}"
domain: "{domain}"
area: "{area}"
systems: []
links: []
---

"""


def guess_artifact_type(name: str) -> str:
    n = name.lower()
    if n.startswith("sop-"):
        return "sop"
    if n.startswith("proc-") or "proceso" in n:
        return "process"
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser(description="Add minimal frontmatter if missing (dry-run by default)")
    parser.add_argument("dir", help="Directory to scan")
    parser.add_argument("--apply", action="store_true", help="Write changes (default dry-run)")
    parser.add_argument("--owner", default="Knowledge Management")
    parser.add_argument("--approver", default="Governance")
    parser.add_argument("--criticality", default="medium")
    parser.add_argument("--domain", default="operations")
    parser.add_argument("--area", default="general")
    parser.add_argument("--sla", type=int, default=6)
    args = parser.parse_args()

    root = Path(args.dir).resolve()
    today = datetime.utcnow().date()
    next_dt = today + timedelta(days=30 * args.sla)

    changed = 0
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        if text.lstrip().startswith("---\n"):
            continue
        title = (text.splitlines()[0].strip("# ") if text else p.stem)
        fm = FM_TEMPLATE.format(
            title=title[:120],
            artifact_type=guess_artifact_type(p.name),
            code="",
            owner=args.owner,
            approver=args.approver,
            criticality=args.criticality,
            sla=args.sla,
            last_review=today.strftime("%Y-%m-%d"),
            next_review=next_dt.strftime("%Y-%m-%d"),
            domain=args.domain,
            area=args.area,
        )
        if args.apply:
            p.write_text(fm + text, encoding="utf-8")
            changed += 1
        else:
            print(f"[DRY-RUN] Would add frontmatter to: {p}")
    print({"ok": True, "changed": changed, "apply": args.apply})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


