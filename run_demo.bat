@echo off
setlocal enableextensions enabledelayedexpansion

set DEMO=%1
if "%DEMO%"=="" set DEMO=ultimate_launch_demo.py

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Attempting install via winget...
  where winget >nul 2>nul || (echo winget not available. Install Python manually and re-run.& exit /b 1)
  winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
)

if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv || python3 -m venv .venv
)

call .venv\Scripts\activate.bat || (echo Failed to activate venv.& exit /b 1)

if exist requirements.txt (
  echo Installing dependencies...
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
)

echo Running demo: %DEMO%
python %DEMO%









