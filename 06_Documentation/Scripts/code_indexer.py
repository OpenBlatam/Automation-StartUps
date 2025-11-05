#!/usr/bin/env python3
import re
import sys
import json
from pathlib import Path
from typing import Optional


RE_FRONT_CODE = re.compile(r"^code:\s*\"?([A-Za-z]+-\d+)\"?", re.IGNORECASE | re.MULTILINE)


def extract_code(path: Path, text: str) -> Optional[str]:
    m = RE_FRONT_CODE.search(text)
    if m:
        return m.group(1)
    # fallback: detect in filename
    m2 = re.search(r"\b([A-Za-z]+-\d+)\b", path.name)
    return m2.group(1) if m2 else None


def classify(path: Path) -> str:
    n = path.name.lower()
    if n.startswith("sop-"):
        return "sop"
    if n.startswith("proc-"):
        return "process"
    return "other"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: code_indexer.py <sgci_root_dir>")
        return 2
    root = Path(sys.argv[1]).resolve()
    items = []
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        code = extract_code(p, text)
        if not code:
            continue
        items.append({
            "code": code.upper(),
            "type": classify(p),
            "path": str(p.relative_to(root)),
            "title": (text.splitlines()[0] if text else p.stem)[:120]
        })

    items.sort(key=lambda x: (x["code"], x["type"]))

    out_dir = root.parent / "Reports_analytics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "code_index.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown
    lines = ["# Índice por Código (PROC/SOP)", "", "code | type | path | title", "--- | --- | --- | ---"]
    for it in items:
        lines.append(f"{it['code']} | {it['type']} | {it['path']} | {it['title']}")
    (out_dir / "code_index.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": True, "count": len(items)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



