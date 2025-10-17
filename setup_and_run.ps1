param(
  [string]$Demo="run_ultimate_ai_demo.py",
  [string[]]$Extras=@()
)

$ErrorActionPreference = "Stop"

function Ensure-Python {
  Write-Host "Checking Python..."
  $python = (Get-Command python -ErrorAction SilentlyContinue)
  if (-not $python) {
    $python3 = (Get-Command python3 -ErrorAction SilentlyContinue)
    if ($python3) { return "python3" }
    Write-Host "Python not found. Installing via winget..." -ForegroundColor Yellow
    $winget = (Get-Command winget -ErrorAction SilentlyContinue)
    if (-not $winget) { throw "winget is not available. Please install Python 3.11+ from Microsoft Store or python.org" }
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements --silent
    $python = (Get-Command python -ErrorAction SilentlyContinue)
    if (-not $python) { throw "Python installation may require a new terminal. Close and reopen PowerShell, then retry." }
  }
  return "python"
}

function Ensure-Venv($py) {
  if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    & $py -m venv .venv
  }
  $envPath = Join-Path (Get-Location) ".venv"
  $activate = Join-Path $envPath "Scripts\Activate.ps1"
  if (-not (Test-Path $activate)) { throw "Venv activation script not found: $activate" }
  Write-Host "Activating virtual environment..."
  . $activate
}

function Install-Requirements {
  Write-Host "Installing dependencies..." -ForegroundColor Cyan
  pip install --upgrade pip
  if (Test-Path "requirements-base.txt") {
    pip install -r requirements-base.txt
  } elseif (Test-Path "requirements.txt") {
    pip install -r requirements.txt
  } else {
    Write-Host "No requirements file found" -ForegroundColor Yellow
  }
  foreach ($extra in $Extras) {
    $file = "requirements-extras-$extra.txt"
    if (Test-Path $file) {
      Write-Host "Installing extra: $extra" -ForegroundColor Cyan
      try { pip install -r $file } catch { Write-Warning "Failed to install extra $extra. Continuing..." }
    } else {
      Write-Warning "Extra file not found: $file"
    }
  }
}

function Run-Demo($py, $demo) {
  if (-not (Test-Path $demo)) { throw "Demo file not found: $demo" }
  Write-Host "Running demo: $demo" -ForegroundColor Green
  & $py $demo
}

try {
  $py = Ensure-Python
  Ensure-Venv $py
  Install-Requirements
  Run-Demo $py $Demo
}
catch {
  Write-Error $_
  Write-Host "You can run a specific demo, e.g.:" -ForegroundColor Yellow
  Write-Host "  powershell -ExecutionPolicy Bypass -File setup_and_run.ps1 -Demo ultimate_launch_demo.py -Extras ml,api,quantum" -ForegroundColor Yellow
  Write-Host "Other demos: FINAL_ULTIMATE_DEMO.py, ULTIMATE_FINAL_DEMO.py, metaverse_launch_platform.py" -ForegroundColor Yellow
}

