# Windows Quick Start

This project includes multiple demos. Use these scripts to install Python, set up a virtual environment, install dependencies, and run a demo automatically.

## Option A: PowerShell (recommended)

Open PowerShell in the project folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1 -Demo smoke_demo.py
```

Validate environment with the smoke demo first (fast), then run the Ultimate AI Demo:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1 -Demo run_ultimate_ai_demo.py -Extras ml
```

Or run the complete Ultimate AI Demo directly:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_and_run.ps1
```

To run other demos, change `-Demo` to one of:
- `FINAL_ULTIMATE_DEMO.py`
- `ULTIMATE_FINAL_DEMO.py`
- `metaverse_launch_platform.py`
- `conscious_ai_launch_system.py`
- `neural_interface_launch_system.py`
- `agi_launch_system.py`

The script will:
- Install Python 3.11 via winget if missing
- Create and activate `.venv`
- Install `requirements.txt`
- Run the selected demo

## Option B: Command Prompt (.bat)

From Command Prompt in the project folder:

```bat
run_demo.bat ultimate_launch_demo.py
```

If Python is missing, the script attempts installation via winget, creates `.venv`, installs dependencies, and runs the demo.

## Troubleshooting
- If winget is unavailable, install Python 3.11+ from Microsoft Store or `python.org`, reopen the terminal, and rerun.
- If execution policy blocks scripts: run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
```

- If heavy packages fail to build (e.g., `qiskit`): temporarily comment them in `requirements.txt`, install the rest, then try installing them separately.
- Ensure GPU drivers/CUDA are installed if you enable GPU-accelerated packages.

