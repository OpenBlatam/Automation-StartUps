#!/usr/bin/env python3

import csv
import pathlib
import sys
import urllib.parse


REQUIRED_FIELDS = [
    "base_url",
    "utm_source",
    "utm_medium",
    "utm_campaign",
]

OPTIONAL_FIELDS = ["utm_content", "utm_term"]


def build_final_url(row: dict) -> str:
    base_url = (row.get("base_url") or "").strip()
    if not base_url:
        return ""

    params = {
        "utm_source": row.get("utm_source", "").strip(),
        "utm_medium": row.get("utm_medium", "").strip(),
        "utm_campaign": row.get("utm_campaign", "").strip(),
    }
    if row.get("utm_content"):
        params["utm_content"] = row["utm_content"].strip()
    if row.get("utm_term"):
        params["utm_term"] = row["utm_term"].strip()

    # Lowercase all values
    params = {k: v.lower() for k, v in params.items() if v}

    # Compose
    parsed = urllib.parse.urlparse(base_url)
    query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    query.update(params)
    new_query = urllib.parse.urlencode(query)
    final = parsed._replace(query=new_query)
    return urllib.parse.urlunparse(final)


def validate_row(row: dict) -> list:
    issues = []
    # Required
    for f in REQUIRED_FIELDS:
        if not (row.get(f) or "").strip():
            issues.append(f"Falta {f}")

    # Lowercase and no spaces for utm fields
    for f in ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]:
        val = (row.get(f) or "").strip()
        if val:
            if any(c.isupper() for c in val) or (" " in val):
                issues.append(f"{f} debe ir en minusculas_sin_espacios: '{val}'")

    # final_url basic check
    final_url = (row.get("final_url") or "").strip()
    if final_url and "?utm_" not in final_url:
        issues.append("final_url no contiene UTMs")

    return issues


def process_csv(path: pathlib.Path) -> int:
    changed = 0
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        # Ensure columns present
        if "final_url" not in fieldnames:
            fieldnames.append("final_url")
        if "shortlink" not in fieldnames:
            fieldnames.append("shortlink")

        for row in reader:
            # Skip comment lines preserved by DictReader? (none), but handle blanks
            if not any((row.get(k) or "").strip() for k in fieldnames):
                rows.append(row)
                continue

            # Build final_url if empty
            if not (row.get("final_url") or "").strip():
                fu = build_final_url(row)
                if fu:
                    row["final_url"] = fu
                    changed += 1

            # Collect issues
            issues = validate_row(row)
            row["_issues"] = "; ".join(issues)
            rows.append(row)

    # Write back (preserving added columns and issues)
    out_fields = list(reader.fieldnames or [])
    if "final_url" not in out_fields:
        out_fields.append("final_url")
    if "shortlink" not in out_fields:
        out_fields.append("shortlink")
    if "_issues" not in out_fields:
        out_fields.append("_issues")

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    return changed


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Uso: python utm_tools.py OUTREACH_UTM_CATALOG.csv [OUTREACH_UTM_CATALOG_REAL_ESTATE_ZONES.csv]")
        return 2
    total_changed = 0
    for p in argv[1:]:
        path = pathlib.Path(p)
        if not path.exists():
            print(f"No existe: {path}")
            continue
        changed = process_csv(path)
        total_changed += changed
        print(f"{path.name}: {changed} final_url generadas/actualizadas")
    return 0 if total_changed >= 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))





