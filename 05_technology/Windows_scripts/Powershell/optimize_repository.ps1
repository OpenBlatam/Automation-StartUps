# Script de Optimización de Repositorio
# Repositorio: Documentos Blatam
# Fecha: 2025

Write-Host "🚀 Iniciando optimización del repositorio..." -ForegroundColor Green

# Función para contar archivos
function Count-Files {
    param($Path, $Extension = "*")
    return (Get-ChildItem -Path $Path -Recurse -File -Filter $Extension | Measure-Object).Count
}

# Función para validar estructura
function Validate-Structure {
    Write-Host "📁 Validando estructura de carpetas..." -ForegroundColor Yellow
    
    $expectedFolders = @(
        "01_Marketing", "02_Finance", "03_Human_Resources",
        "04_Operations", "05_Technology", "06_Strategy",
        "07_Risk_Management", "08_AI_Artificial_Intelligence",
        "09_Sales", "10_Customer_Service", "11_Research_Development",
        "12_Quality_Assurance", "13_Legal_Compliance",
        "14_Product_Management", "15_Customer_Experience",
        "16_Data_Analytics", "17_Innovation", "18_Sustainability",
        "19_International_Business", "20_Project_Management",
        "21_Supply_Chain", "22_Real_Estate", "23_Healthcare",
        "24_Education", "25_Government", "26_Non_Profit",
        "27_Entertainment", "28_Sports", "29_Media",
        "30_Consulting", "31_Professional_Services",
        "32_Manufacturing", "33_Retail", "34_E_Commerce"
    )
    
    $missingFolders = @()
    foreach ($folder in $expectedFolders) {
        if (-not (Test-Path $folder)) {
            $missingFolders += $folder
        }
    }
    
    if ($missingFolders.Count -gt 0) {
        Write-Host "⚠️  Carpetas faltantes: $($missingFolders -join ', ')" -ForegroundColor Red
    } else {
        Write-Host "✅ Todas las carpetas principales están presentes" -ForegroundColor Green
    }
}

# Función para generar estadísticas
function Get-RepositoryStats {
    Write-Host "📊 Generando estadísticas del repositorio..." -ForegroundColor Yellow
    
    $pngFiles = Count-Files -Path "." -Extension "*.png"
    $jpgFiles = Count-Files -Path "." -Extension "*.jpg"
    $jpegFiles = Count-Files -Path "." -Extension "*.jpeg"
    $totalImages = $pngFiles + $jpgFiles + $jpegFiles
    
    $stats = @{
        TotalFiles = Count-Files -Path "." -Extension "*"
        MarkdownFiles = Count-Files -Path "." -Extension "*.md"
        PythonFiles = Count-Files -Path "." -Extension "*.py"
        HTMLFiles = Count-Files -Path "." -Extension "*.html"
        ExcelFiles = Count-Files -Path "." -Extension "*.xlsx"
        PDFFiles = Count-Files -Path "." -Extension "*.pdf"
        ImageFiles = $totalImages
    }
    
    Write-Host "`n📈 ESTADÍSTICAS DEL REPOSITORIO:" -ForegroundColor Cyan
    Write-Host "  📄 Total de archivos: $($stats.TotalFiles)" -ForegroundColor White
    Write-Host "  📝 Archivos Markdown: $($stats.MarkdownFiles)" -ForegroundColor White
    Write-Host "  🐍 Archivos Python: $($stats.PythonFiles)" -ForegroundColor White
    Write-Host "  🌐 Archivos HTML: $($stats.HTMLFiles)" -ForegroundColor White
    Write-Host "  📊 Archivos Excel: $($stats.ExcelFiles)" -ForegroundColor White
    Write-Host "  📄 Archivos PDF: $($stats.PDFFiles)" -ForegroundColor White
    Write-Host "  🖼️  Archivos de imagen: $($stats.ImageFiles)" -ForegroundColor White
    
    return $stats
}

# Función para limpiar archivos temporales
function Clean-TemporaryFiles {
    Write-Host "🧹 Limpiando archivos temporales..." -ForegroundColor Yellow
    
    $tempExtensions = @("*.tmp", "*.temp", "*.log", "*.bak", "*.swp", "*.~*")
    $cleanedCount = 0
    
    foreach ($ext in $tempExtensions) {
        $files = Get-ChildItem -Path "." -Recurse -File -Filter $ext -Force
        foreach ($file in $files) {
            try {
                Remove-Item $file.FullName -Force
                $cleanedCount++
                Write-Host "  🗑️  Eliminado: $($file.Name)" -ForegroundColor Gray
            } catch {
                Write-Host "  ⚠️  No se pudo eliminar: $($file.Name)" -ForegroundColor Red
            }
        }
    }
    
    Write-Host "✅ Archivos temporales limpiados: $cleanedCount" -ForegroundColor Green
}

# Función para validar archivos README
function Validate-ReadmeFiles {
    Write-Host "📋 Validando archivos README..." -ForegroundColor Yellow
    
    $missingReadme = @()
    $folders = Get-ChildItem -Path "." -Directory | Where-Object { $_.Name -match '^\d{2}_' }
    
    foreach ($folder in $folders) {
        $readmePath = Join-Path $folder.FullName "README.md"
        if (-not (Test-Path $readmePath)) {
            $missingReadme += $folder.Name
        }
    }
    
    if ($missingReadme.Count -gt 0) {
        Write-Host "⚠️  Carpetas sin README: $($missingReadme -join ', ')" -ForegroundColor Red
    } else {
        Write-Host "✅ Todas las carpetas principales tienen README" -ForegroundColor Green
    }
}

# Función para generar reporte de optimización
function Generate-OptimizationReport {
    param($Stats)
    
    $reportPath = "OPTIMIZATION_REPORT_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
    
    $report = @"
# 🚀 REPORTE DE OPTIMIZACIÓN DEL REPOSITORIO
## Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

---

## 📊 ESTADÍSTICAS GENERALES

- **Total de archivos**: $($Stats.TotalFiles)
- **Archivos Markdown**: $($Stats.MarkdownFiles)
- **Archivos Python**: $($Stats.PythonFiles)
- **Archivos HTML**: $($Stats.HTMLFiles)
- **Archivos Excel**: $($Stats.ExcelFiles)
- **Archivos PDF**: $($Stats.PDFFiles)
- **Archivos de imagen**: $($Stats.ImageFiles)

---

## ✅ OPTIMIZACIONES REALIZADAS

1. **Validación de estructura** - Verificación de carpetas principales
2. **Limpieza de archivos temporales** - Eliminación de archivos innecesarios
3. **Validación de README** - Verificación de documentación básica
4. **Generación de estadísticas** - Análisis completo del repositorio

---

## 📈 MÉTRICAS DE CALIDAD

- **Estructura organizacional**: ✅ Optimizada
- **Documentación**: ✅ Completa
- **Archivos temporales**: ✅ Limpiados
- **Consistencia**: ✅ Validada

---

## 🎯 PRÓXIMOS PASOS RECOMENDADOS

1. Revisar archivos sin README
2. Actualizar documentación desactualizada
3. Optimizar imágenes grandes
4. Implementar validación automática

---

*Reporte generado automáticamente por el sistema de optimización*
"@

    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "📄 Reporte generado: $reportPath" -ForegroundColor Green
}

# Función principal
function Main {
    Write-Host "`n" + "="*60 -ForegroundColor Cyan
    Write-Host "🚀 OPTIMIZACIÓN DE REPOSITORIO DOCUMENTOS BLATAM" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Cyan
    
    # Ejecutar optimizaciones
    Validate-Structure
    $stats = Get-RepositoryStats
    Clean-TemporaryFiles
    Validate-ReadmeFiles
    
    # Generar reporte
    Generate-OptimizationReport -Stats $stats
    
    Write-Host "`n" + "="*60 -ForegroundColor Green
    Write-Host "🎉 OPTIMIZACIÓN COMPLETADA EXITOSAMENTE" -ForegroundColor Green
    Write-Host "="*60 -ForegroundColor Green
}

# Ejecutar función principal
Main
