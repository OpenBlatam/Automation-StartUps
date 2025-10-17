#!/usr/bin/env python3
"""
ClickUp Brain Unified CLI Runner
===============================

Launch any ClickUp Brain subsystem from a single command.
"""

import sys
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent

    SUBSYSTEM_SCRIPTS = {
        "api": "clickup_brain_api.py",
        "dashboard": "clickup_brain_dashboard.py",
        "mobile": "clickup_brain_mobile.py",
        "ai": "clickup_brain_ai_assistant.py",
        "blockchain": "clickup_brain_blockchain.py",
        "iot": "clickup_brain_iot.py",
        "arvr": "clickup_brain_ar_vr.py",
        "quantum": "clickup_brain_quantum.py",
        "neural": "clickup_brain_neural_interface.py",
        "metaverse": "clickup_brain_metaverse.py",
        "holographic": "clickup_brain_holographic.py",
        "telepathic": "clickup_brain_telepathic.py",
        "timetravel": "clickup_brain_time_travel.py",
        "dimensions": "clickup_brain_dimension_hopping.py",
        "config": "clickup_brain_config.py",
        "logging": "clickup_brain_logging.py",
        "errors": "clickup_brain_error_handling.py",
        "performance": "clickup_brain_performance.py",
        "plugins": "clickup_brain_plugin_system.py",
        "gateway": "clickup_brain_api_gateway.py",
        "cache": "clickup_brain_caching.py",
        "queue": "clickup_brain_message_queue.py",
        "database": "clickup_brain_database_orm.py",
        "testing": "clickup_brain_testing_framework.py",
        "deployment": "clickup_brain_deployment.py",
        "monitoring": "clickup_brain_monitoring.py",
        "security": "clickup_brain_security.py",
        "analytics": "clickup_brain_analytics.py",
        "workflow": "clickup_brain_workflow.py",
        "integration": "clickup_brain_integration.py",
        "connectors": "clickup_brain_connectors.py",
        "ai_ml": "clickup_brain_ai_ml_advanced.py",
        "realtime": "clickup_brain_realtime_analytics.py",
        "automation": "clickup_brain_intelligent_automation.py",
        "predictive": "clickup_brain_predictive_insights.py",
        "quantum": "clickup_brain_quantum_ai.py",
        "transcendent": "clickup_brain_transcendent_intelligence.py",
        "divine": "clickup_brain_divine_ai.py",
        "infinite": "clickup_brain_infinite_ai.py",
        "omniversal": "clickup_brain_omniversal_ai.py",
        "eternal": "clickup_brain_eternal_ai.py",
        "absolute": "clickup_brain_absolute_ai.py",
        "supreme": "clickup_brain_supreme_ai.py",
        "ultimate": "clickup_brain_ultimate_ai.py",
        "perfect": "clickup_brain_perfect_ai.py",
        "flawless": "clickup_brain_flawless_ai.py",
        "impeccable": "clickup_brain_impeccable_ai.py",
        "flawless_supremacy": "clickup_brain_flawless_supremacy.py",
        "impeccable_supremacy": "clickup_brain_impeccable_supremacy.py",
        "perfect_supremacy": "clickup_brain_perfect_supremacy.py",
        "transcendent_perfection": "clickup_brain_transcendent_perfection.py",
        "divine_supremacy": "clickup_brain_divine_supremacy.py",
        "cosmic_consciousness": "clickup_brain_cosmic_consciousness.py",
        "eternal_perfection": "clickup_brain_eternal_perfection.py",
        "infinite_supremacy": "clickup_brain_infinite_supremacy.py",
        "absolute_transcendence": "clickup_brain_absolute_transcendence.py",
        "supreme_transcendence": "clickup_brain_supreme_transcendence.py",
        "omnipotent_evolution": "clickup_brain_omnipotent_evolution.py",
        "infinite_consciousness": "clickup_brain_infinite_consciousness.py",
        "eternal_supremacy": "clickup_brain_eternal_supremacy.py",
        "divine_transcendence": "clickup_brain_divine_transcendence.py",
        "absolute_omnipotence": "clickup_brain_absolute_omnipotence.py",
        "ultimate_mastery": "clickup_brain_ultimate_mastery.py",
        "infinite_evolution": "clickup_brain_infinite_evolution.py",
        "supreme_consciousness": "clickup_brain_supreme_consciousness.py",
        "eternal_transcendence": "clickup_brain_eternal_transcendence.py",
        "absolute_perfection": "clickup_brain_absolute_perfection.py",
        "infinite_mastery": "clickup_brain_infinite_mastery.py"
    }


def run_script(script_name: str, extra_args: list[str], python_exe: str, dry_run: bool) -> int:
    path = ROOT / script_name
    if not path.exists():
        print(f"Error: script not found: {path}")
        return 1
    cmd = [python_exe, str(path), *extra_args]
    if dry_run:
        print("DRY-RUN:", " ".join(cmd))
        return 0
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("Error: Python interpreter not found:", python_exe)
        return 1


def check_subsystems() -> int:
    """Verify subsystem scripts exist and can be imported."""
    import importlib.util
    ok = True
    for name, script in sorted(SUBSYSTEM_SCRIPTS.items()):
        script_path = ROOT / script
        if not script_path.exists():
            print(f"[MISSING] {name}: {script_path}")
            ok = False
            continue
        spec = importlib.util.spec_from_file_location(name, script_path)
        try:
            module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(module)
            print(f"[OK] {name}")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            ok = False
    return 0 if ok else 1


def read_version() -> str:
    version_file = ROOT / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ClickUp Brain Unified CLI")
    parser.add_argument("subsystem", nargs="?", choices=sorted(SUBSYSTEM_SCRIPTS.keys()), help="Subsystem to run")
    parser.add_argument("--", dest="double_dash", nargs=argparse.REMAINDER, help="Args passed to subsystem")
    parser.add_argument("-l", "--list", action="store_true", help="List available subsystems and exit")
    parser.add_argument("-c", "--check", action="store_true", help="Validate subsystem availability and imports")
    parser.add_argument("--python", dest="python_exe", default=sys.executable, help="Python interpreter to use")
    parser.add_argument("--dry-run", action="store_true", help="Print the command that would run and exit")
    parser.add_argument("-v", "--version", action="store_true", help="Print version and exit")
    args = parser.parse_args(argv)

    if args.version:
        print(read_version())
        return 0

    if args.check:
        return check_subsystems()

    if args.list or args.subsystem is None:
        print("Available subsystems:")
        for name in sorted(SUBSYSTEM_SCRIPTS.keys()):
            print(f"  - {name}")
        return 0

    extra = args.double_dash or []
    return run_script(SUBSYSTEM_SCRIPTS[args.subsystem], extra, args.python_exe, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
