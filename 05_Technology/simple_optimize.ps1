# Script Simple de Optimización
Write-Host "🚀 Iniciando optimización simple..." -ForegroundColor Green

# Contar archivos
$totalFiles = (Get-ChildItem -Recurse -File | Measure-Object).Count
$mdFiles = (Get-ChildItem -Recurse -File -Filter "*.md" | Measure-Object).Count
$pyFiles = (Get-ChildItem -Recurse -File -Filter "*.py" | Measure-Object).Count

Write-Host "📊 ESTADÍSTICAS:" -ForegroundColor Cyan
Write-Host "  Total archivos: $totalFiles" -ForegroundColor White
Write-Host "  Archivos MD: $mdFiles" -ForegroundColor White
Write-Host "  Archivos PY: $pyFiles" -ForegroundColor White

# Validar carpetas principales
$mainFolders = @("01_Marketing", "02_Finance", "05_Technology", "08_AI_Artificial_Intelligence")
$missing = @()

foreach ($folder in $mainFolders) {
    if (-not (Test-Path $folder)) {
        $missing += $folder
    }
}

if ($missing.Count -eq 0) {
    Write-Host "✅ Todas las carpetas principales están presentes" -ForegroundColor Green
} else {
    Write-Host "⚠️ Carpetas faltantes: $($missing -join ', ')" -ForegroundColor Red
}

Write-Host "🎉 Optimización completada!" -ForegroundColor Green
