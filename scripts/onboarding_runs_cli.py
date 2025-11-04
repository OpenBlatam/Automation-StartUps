#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def fetch_variable(base_url: str, token: str | None, var_key: str) -> dict[str, Any] | None:
    url = f"{base_url.rstrip('/')}/api/v1/variables/{var_key}"
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch onboarding progress from Airflow Variables")
    parser.add_argument("email", help="Employee email, e.g., ana.romero@example.com")
    parser.add_argument("--airflow", dest="airflow", default=env("AIRFLOW_BASE_URL", "http://localhost:8080"), help="Airflow base URL")
    parser.add_argument("--token", dest="token", default=env("AIRFLOW_TOKEN", ""), help="Airflow API Bearer token")
    args = parser.parse_args()

    var_key = f"onboarding_runs:{args.email}"
    try:
        data = fetch_variable(args.airflow, args.token or None, var_key)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if not data or "value" not in data:
        print("[]")
        return 0

    try:
        # Airflow returns {key:..., value:"..."}
        value = data["value"]
        parsed = json.loads(value)
    except Exception:
        parsed = []

    print(json.dumps(parsed, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




