param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = $env:PYTHON ?? "python"
& $Python "$ScriptDir\clickup_brain_cli.py" @Args
exit $LASTEXITCODE








