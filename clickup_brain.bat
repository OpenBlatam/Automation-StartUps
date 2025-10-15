@echo off
setlocal
set SCRIPT_DIR=%~dp0
set PYTHON_CMD=python
%PYTHON_CMD% "%SCRIPT_DIR%clickup_brain_cli.py" %*
endlocal








