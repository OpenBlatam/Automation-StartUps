Param(
    [switch]$Install,
    [switch]$Discover,
    [string[]]$Include,
    [string[]]$Exclude,
    [string]$Func = "main",
    [string]$Report = "orchestrator_report.md",
    [string]$JsonReport,
    [switch]$Parallel,
    [double]$Timeout,
    [int]$Retries = 0,
    [string]$Env,
    [string]$Config,
    [switch]$FailFast,
    [switch]$RequireAll,
    [string]$LogFile,
    [switch]$DryRun,
    [switch]$Verbose,
    [int]$MaxWorkers = 0,
    [switch]$Health
)

$ErrorActionPreference = "Stop"

Write-Host "=== Run ClickUp Brain Orchestrator ==="
if ($Install) {
    Write-Host "Installing Python dependencies..."
    python -m pip install --upgrade pip
    if (Test-Path requirements_enhanced.txt) {
        python -m pip install -r requirements_enhanced.txt
    } elseif (Test-Path requirements.txt) {
        python -m pip install -r requirements.txt
    } else {
        Write-Host "No requirements file found. Skipping install."
    }
}

if ($Health) {
    Write-Host "Python version:"; python --version
    Write-Host "Pip version:"; python -m pip --version
    Write-Host "Checking key modules presence..."
    Get-ChildItem -Name clickup_brain_*.py | ForEach-Object { Write-Host " - $_" }
    return
}

Write-Host "Starting orchestrator..."
$argsList = @()
if ($Discover) { $argsList += "--discover" }
if ($Include) { $argsList += "--include"; $argsList += $Include }
if ($Exclude) { $argsList += "--exclude"; $argsList += $Exclude }
if ($Func)    { $argsList += "--func"; $argsList += $Func }
if ($Report)  { $argsList += "--report"; $argsList += $Report }
if ($JsonReport) { $argsList += "--json-report"; $argsList += $JsonReport }
if ($Parallel)   { $argsList += "--parallel" }
if ($Timeout)    { $argsList += "--timeout"; $argsList += $Timeout }
if ($Retries -gt 0) { $argsList += "--retries"; $argsList += $Retries }
if ($Env)        { $argsList += "--env"; $argsList += $Env }
if ($Config)     { $argsList += "--config"; $argsList += $Config }
if ($FailFast)   { $argsList += "--fail-fast" }
if ($RequireAll) { $argsList += "--require-all" }
if ($LogFile)    { $argsList += "--logfile"; $argsList += $LogFile }
if ($DryRun)     { $argsList += "--dry-run" }
if ($Verbose)    { $argsList += "--verbose" }
if ($MaxWorkers -gt 0) { $argsList += "--max-workers"; $argsList += $MaxWorkers }

python clickup_brain_orchestrator.py @argsList


