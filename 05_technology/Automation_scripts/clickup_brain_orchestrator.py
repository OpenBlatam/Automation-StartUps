#!/usr/bin/env python3
"""
ClickUp Brain - Orchestrator
Runs available ClickUp Brain modules in sequence with safe fallbacks.
"""

import importlib
import sys
import argparse
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from datetime import datetime

MODULES_IN_ORDER = [
    ("clickup_brain_workflow_automation", "main"),
    ("clickup_brain_ultimate_ai", "main"),
]

def run_module(module_name: str, func_name: str) -> tuple[bool, float, str]:
    try:
        mod = importlib.import_module(module_name)
        func = getattr(mod, func_name, None)
        if callable(func):
            print(f"[Orchestrator] Running {module_name}.{func_name}()...")
            start = time.perf_counter()
            result = func()
            duration = time.perf_counter() - start
            print(f"[Orchestrator] {module_name} completed in {duration:.2f}s with: {result}")
            return True, duration, "ok"
        print(f"[Orchestrator] {module_name}.{func_name} not found, skipping.")
        return False, 0.0, "func_not_found"
    except Exception as e:
        print(f"[Orchestrator] Error running {module_name}: {e}")
        return False, 0.0, str(e)

def discover_modules(directory: Path) -> list[str]:
    names: list[str] = []
    for p in sorted(directory.glob("clickup_brain_*.py")):
        if p.name == Path(__file__).name:
            continue
        names.append(p.stem)
    return names

def write_markdown_report(path: Path, runs: list[dict]):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines = [
        f"# ClickUp Brain Orchestrator Report",
        f"\n**Generated:** {ts}\n",
        "\n| Module | Status | Duration (s) |",
        "|---|---:|---:|",
    ]
    for r in runs:
        lines.append(f"| {r['module']} | {r['status']} | {r['duration']:.2f} |")
    total = sum(r['duration'] for r in runs)
    ok = sum(1 for r in runs if r['ok'])
    lines.append(f"\n**Summary:** {ok}/{len(runs)} succeeded. Total: {total:.2f}s")
    path.write_text("\n".join(lines), encoding="utf-8")

def write_json_report(path: Path, runs: list[dict]):
    report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total": len(runs),
            "succeeded": sum(1 for r in runs if r.get("ok")),
            "failed": sum(1 for r in runs if not r.get("ok")),
            "total_duration_sec": sum(r.get("duration", 0.0) for r in runs),
        },
        "runs": runs,
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        import os
        os.environ.setdefault(key.strip(), val.strip())

class TeeLogger:
    def __init__(self, logfile: Path | None):
        self.logfile = logfile
        self._fh = logfile.open("a", encoding="utf-8") if logfile else None
    def write(self, message: str):
        message = str(message)
        sys.__stdout__.write(message)
        if self._fh:
            self._fh.write(message)
            self._fh.flush()
    def flush(self):
        sys.__stdout__.flush()
        if self._fh:
            self._fh.flush()
    def close(self):
        if self._fh:
            self._fh.close()

def main() -> int:
    parser = argparse.ArgumentParser(description="ClickUp Brain Orchestrator")
    parser.add_argument("--discover", action="store_true", help="Discover modules dynamically")
    parser.add_argument("--include", nargs="*", default=None, help="Explicit module names to include")
    parser.add_argument("--exclude", nargs="*", default=None, help="Module names to exclude")
    parser.add_argument("--func", default="main", help="Function name to call in each module")
    parser.add_argument("--report", default="orchestrator_report.md", help="Markdown report output path")
    parser.add_argument("--json-report", default=None, help="Optional JSON report output path")
    parser.add_argument("--parallel", action="store_true", help="Run modules in parallel")
    parser.add_argument("--timeout", type=float, default=None, help="Per-module timeout in seconds")
    parser.add_argument("--retries", type=int, default=0, help="Retries per module on failure/timeout")
    parser.add_argument("--env", default=None, help="Optional .env file to load")
    parser.add_argument("--dry-run", action="store_true", help="Plan and print modules without executing")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging output")
    parser.add_argument("--max-workers", type=int, default=0, help="Max parallel workers (default=min(4, N))")
    parser.add_argument("--config", default=None, help="Optional JSON config file")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure (sequential mode)")
    parser.add_argument("--require-all", action="store_true", help="Exit non-zero unless all modules succeed")
    parser.add_argument("--logfile", default=None, help="Tee console output to this file")
    args = parser.parse_args()

    tee = TeeLogger(Path(args.logfile)) if args.logfile else None
    if tee:
        sys.stdout = tee  # type: ignore
    try:
        print("=== ClickUp Brain Orchestrator ===")
        print(datetime.now().isoformat())

        if args.env:
            load_env_file(Path(args.env))

        modules: list[str]
        effective = {}
        # Load config file (optional)
        if args.config:
            cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
            effective.update(cfg if isinstance(cfg, dict) else {})
        # CLI overrides
        if args.discover is not None:
            effective["discover"] = args.discover
        if args.include is not None:
            effective["include"] = args.include
        if args.exclude is not None:
            effective["exclude"] = args.exclude
        if args.func:
            effective["func"] = args.func
        if args.parallel:
            effective["parallel"] = True
        if args.timeout is not None:
            effective["timeout"] = args.timeout
        if args.retries is not None:
            effective["retries"] = args.retries
        if args.fail_fast:
            effective["fail_fast"] = True
        if args.require_all:
            effective["require_all"] = True

        discover_flag = bool(effective.get("discover", False))
        include_cfg = effective.get("include")
        exclude_cfg = effective.get("exclude")
        func_name = effective.get("func", args.func)
        parallel_flag = bool(effective.get("parallel", args.parallel))
        timeout_val = effective.get("timeout", args.timeout)
        retries_val = int(effective.get("retries", args.retries))
        fail_fast = bool(effective.get("fail_fast", False))
        require_all = bool(effective.get("require_all", False))
        dry_run = bool(effective.get("dry_run", args.dry_run))
        verbose = bool(effective.get("verbose", args.verbose))
        max_workers = int(effective.get("max_workers", args.max_workers)) if effective.get("max_workers", args.max_workers) is not None else 0

        if discover_flag:
            modules = discover_modules(Path.cwd())
        else:
            modules = [m for m, _ in MODULES_IN_ORDER]

        if include_cfg:
            modules = [m for m in modules if m in set(include_cfg)]
        if exclude_cfg:
            modules = [m for m in modules if m not in set(exclude_cfg)]

        if verbose:
            print(f"[Orchestrator] Modules selected: {modules}")
            print(f"[Orchestrator] Options -> parallel={parallel_flag} timeout={timeout_val} retries={retries_val} fail_fast={fail_fast} require_all={require_all} dry_run={dry_run} max_workers={max_workers}")

        if dry_run:
            runs = [{"module": m, "ok": True, "duration": 0.0, "status": "dry_run"} for m in modules]
            write_markdown_report(Path(args.report), runs)
            if args.json_report:
                write_json_report(Path(args.json_report), runs)
            print("[Orchestrator] Dry-run complete. Reports generated.")
            return 0

    def run_with_retries(name: str):
        attempts = 0
        last = {"ok": False, "duration": 0.0, "status": "not_run"}
        while attempts <= retries_val:
            attempts += 1
            with ThreadPoolExecutor(max_workers=1) as exec_single:
                fut = exec_single.submit(run_module, name, func_name)
                try:
                    ok, duration, status = fut.result(timeout=timeout_val) if timeout_val else fut.result()
                except TimeoutError:
                    ok, duration, status = False, 0.0, "timeout"
                last = {"ok": ok, "duration": duration, "status": status, "attempt": attempts}
                if ok:
                    break
        return {"module": name, **last}

    runs: list[dict] = []
    if parallel_flag and modules:
        workers = max_workers if max_workers and max_workers > 0 else min(4, len(modules))
        if verbose:
            print(f"[Orchestrator] Running in parallel with {workers} workers")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_map = {pool.submit(run_with_retries, m): m for m in modules}
            for fut in as_completed(future_map):
                runs.append(fut.result())
    else:
        for m in modules:
            r = run_with_retries(m)
            runs.append(r)
            if fail_fast and not r.get("ok"):
                print(f"[Orchestrator] Fail-fast triggered on {m}")
                break

    successes = sum(1 for r in runs if r.get("ok"))

    write_markdown_report(Path(args.report), runs)
    print(f"[Orchestrator] Report written to {args.report}")
    if args.json_report:
        write_json_report(Path(args.json_report), runs)
        print(f"[Orchestrator] JSON report written to {args.json_report}")
    print(f"[Orchestrator] Finished. Successful modules: {successes}/{len(runs)}")
    exit_ok = (successes > 0) if not require_all else (successes == len(runs))
    return 0 if exit_ok else 1
    finally:
        if tee:
            tee.close()

if __name__ == "__main__":
    sys.exit(main())


