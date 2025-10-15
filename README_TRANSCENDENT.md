# ClickUp Brain Transcendent Layer

Quick-start guide to run transcendent subsystems (Time Travel, Dimension Hopping, Neural, Metaverse, Holographic, Telepathic).

## Prerequisites
- Python 3.10+
- Install project dependencies (selectively):
  - For docs and local demos, many modules run with Python stdlib only.
  - Advanced features may require extras listed in existing requirement files.

## Unified CLI
```bash
python clickup_brain_cli.py --version
python clickup_brain_cli.py --list
python clickup_brain_cli.py --check
python clickup_brain_cli.py --dry-run neural
python clickup_brain_cli.py --python C:\\Python310\\python.exe timetravel
python clickup_brain_cli.py timetravel
python clickup_brain_cli.py dimensions
python clickup_brain_cli.py neural
python clickup_brain_cli.py metaverse
python clickup_brain_cli.py holographic
python clickup_brain_cli.py telepathic
```

Pass additional args to underlying scripts by adding `--` and then the args.
```bash
python clickup_brain_cli.py timetravel -- --help
```

## Healthcheck
```bash
python clickup_brain_healthcheck.py
```

## Windows Runners
```bat
clickup_brain.bat --list
clickup_brain.bat --check
powershell -ExecutionPolicy Bypass -File .\\clickup_brain.ps1 --list
```

## Troubleshooting
- If "Python was not found", install Python and ensure it is in PATH.
- Run from the workspace root: `C:\\Users\\blatam\\Documents\\documentos_blatam`.
- Subsystems print their status to the console when run.
