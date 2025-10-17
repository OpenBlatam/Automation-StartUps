#!/usr/bin/env python3
"""
ClickUp Brain Healthcheck

Verifies Python version, optional key packages, and presence of core scripts.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent

CORE_SCRIPTS = [
    "clickup_brain_cli.py",
    "clickup_brain_time_travel.py",
    "clickup_brain_dimension_hopping.py",
    "clickup_brain_neural_interface.py",
]

OPTIONAL_PACKAGES = [
    ("fastapi", "API server"),
    ("plotly", "dashboard"),
    ("dash", "dashboard"),
]


def check_python() -> bool:
    ok = sys.version_info >= (3, 10)
    print(f"Python {sys.version.split()[0]}: {'OK' if ok else 'Upgrade to 3.10+'}")
    return ok


def check_files() -> bool:
    ok = True
    for name in CORE_SCRIPTS:
        path = ROOT / name
        if path.exists():
            print(f"[OK] {name}")
        else:
            print(f"[MISSING] {name}")
            ok = False
    return ok


def check_packages() -> bool:
    ok = True
    for pkg, purpose in OPTIONAL_PACKAGES:
        try:
            __import__(pkg)
            print(f"[OK] {pkg} ({purpose})")
        except Exception:
            print(f"[OPTIONAL] {pkg} not installed ({purpose})")
    return ok


def main() -> int:
    ok_python = check_python()
    ok_files = check_files()
    _ = check_packages()
    return 0 if (ok_python and ok_files) else 1


if __name__ == "__main__":
    raise SystemExit(main())










