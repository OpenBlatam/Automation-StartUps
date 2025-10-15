import json
from datetime import datetime

def main():
    print("Smoke demo: environment validation")
    # Minimal checks
    checks = {}
    try:
        import numpy as np  # noqa: F401
        checks["numpy"] = "ok"
    except Exception as e:
        checks["numpy"] = f"fail: {e}"
    try:
        import pandas as pd  # noqa: F401
        checks["pandas"] = "ok"
    except Exception as e:
        checks["pandas"] = f"fail: {e}"
    try:
        import sklearn  # noqa: F401
        checks["scikit_learn"] = "ok"
    except Exception as e:
        checks["scikit_learn"] = f"fail: {e}"

    result = {
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
        "status": "ok" if all(v == "ok" for v in checks.values()) else "partial"
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()









