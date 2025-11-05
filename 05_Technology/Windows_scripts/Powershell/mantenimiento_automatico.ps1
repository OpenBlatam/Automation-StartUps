# Script de Mantenimiento Automático para Organización de Documentos
# =================================================================
# 
# Este script automatiza el mantenimiento de la estructura organizacional:
# - Actualiza índices automáticamente
# - Verifica integridad de archivos
# - Genera reportes de estadísticas
# - Mantiene documentación actualizada
#
# Autor: Sistema de Organización Automática
# Versión: 1.0
# Fecha: 2024

param(
    [switch]$FullScan = $false,
    [switch]$UpdateIndexes = $true,
    [switch]$GenerateReport = $true,
    [switch]$CleanTemp = $true
)

$BasePath = "C:\Users\adan\frontier\docuementos"
$LogFile = "$BasePath\scripts\mantenimiento_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

function Get-FileStats {
    param($Path)
    
    $Stats = @{
        TotalFiles = 0
        TotalFolders = 0
        FilesByType = @{}
        FilesByFolder = @{}
        LastUpdate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
    
    Write-Log "🔍 Escaneando estructura de archivos..."
    
    $AllItems = Get-ChildItem -Path $Path -Recurse -Force
    
    foreach ($Item in $AllItems) {
        if ($Item.PSIsContainer) {
            $Stats.TotalFolders++
        } else {
            $Stats.TotalFiles++
            
            # Estadísticas por tipo
            $Extension = $Item.Extension.ToLower()
            if (-not $Stats.FilesByType.ContainsKey($Extension)) {
                $Stats.FilesByType[$Extension] = 0
            }
            $Stats.FilesByType[$Extension]++
            
            # Estadísticas por carpeta
            $FolderName = $Item.Directory.Name
            if (-not $Stats.FilesByFolder.ContainsKey($FolderName)) {
                $Stats.FilesByFolder[$FolderName] = 0
            }
            $Stats.FilesByFolder[$FolderName]++
        }
    }
    
    Write-Log "✅ Escaneo completado: $($Stats.TotalFiles) archivos en $($Stats.TotalFolders) carpetas"
    return $Stats
}

function Test-FileIntegrity {
    param($Path)
    
    Write-Log "🔍 Verificando integridad de archivos..."
    
    $CriticalFiles = @(
        "ORGANIZACION_ARCHIVOS.md",
        "INDICE_BUSQUEDA_GLOBAL.md",
        "ACCESO_RAPIDO.md"
    )
    
    $MissingFiles = @()
    
    foreach ($File in $CriticalFiles) {
        $FilePath = Join-Path $Path $File
        if (-not (Test-Path $FilePath)) {
            $MissingFiles += $File
        }
    }
    
    if ($MissingFiles.Count -gt 0) {
        Write-Log "⚠️  Archivos críticos faltantes: $($MissingFiles -join ', ')" "WARN"
        return $false
    } else {
        Write-Log "✅ Todos los archivos críticos están presentes"
        return $true
    }
}

function Update-OrganizationStats {
    param($Path, $Stats)
    
    $OrgFile = Join-Path $Path "ORGANIZACION_ARCHIVOS.md"
    
    if (Test-Path $OrgFile) {
        Write-Log "📝 Actualizando estadísticas en ORGANIZACION_ARCHIVOS.md..."
        
        $Content = Get-Content $OrgFile -Raw -Encoding UTF8
        $Content = $Content -replace "\*Total de archivos procesados: \d+\*", "*Total de archivos procesados: $($Stats.TotalFiles)*"
        
        Set-Content $OrgFile $Content -Encoding UTF8
        Write-Log "✅ Estadísticas actualizadas"
    }
}

function Update-SearchIndex {
    param($Path, $Stats)
    
    $IndexFile = Join-Path $Path "INDICE_BUSQUEDA_GLOBAL.md"
    
    if (Test-Path $IndexFile) {
        Write-Log "📝 Actualizando índice de búsqueda..."
        
        $Content = Get-Content $IndexFile -Raw -Encoding UTF8
        $Content = $Content -replace "\*Total de archivos indexados: \d+\*", "*Total de archivos indexados: $($Stats.TotalFiles)*"
        
        Set-Content $IndexFile $Content -Encoding UTF8
        Write-Log "✅ Índice de búsqueda actualizado"
    }
}

function New-StatisticsReport {
    param($Path, $Stats)
    
    Write-Log "📊 Generando reporte de estadísticas..."
    
    $ReportContent = @"
# 📊 Reporte de Estadísticas - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## 📈 Resumen General
- **Total de archivos**: $($Stats.TotalFiles)
- **Total de carpetas**: $($Stats.TotalFolders)
- **Última actualización**: $($Stats.LastUpdate)

## 📁 Archivos por Tipo
"@

    foreach ($Type in ($Stats.FilesByType.GetEnumerator() | Sort-Object Key)) {
        $Extension = if ($Type.Key) { $Type.Key } else { "Sin extensión" }
        $ReportContent += "`n- **$Extension**: $($Type.Value) archivos"
    }

    $ReportContent += "`n`n## 📂 Archivos por Carpeta`n"

    foreach ($Folder in ($Stats.FilesByFolder.GetEnumerator() | Sort-Object Value -Descending)) {
        $ReportContent += "- **$($Folder.Key)**: $($Folder.Value) archivos`n"
    }

    $MostCommonType = ($Stats.FilesByType.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1)
    $MostFilesFolder = ($Stats.FilesByFolder.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1)
    $AvgFilesPerFolder = [math]::Round($Stats.TotalFiles / [math]::Max(1, $Stats.TotalFolders), 1)

    $ReportContent += @"

## 🔍 Análisis de Distribución
- **Archivos más comunes**: $($MostCommonType.Key) ($($MostCommonType.Value) archivos)
- **Carpeta con más archivos**: $($MostFilesFolder.Key) ($($MostFilesFolder.Value) archivos)
- **Promedio de archivos por carpeta**: $AvgFilesPerFolder

---
*Reporte generado automáticamente por el sistema de mantenimiento*
"@

    $ReportPath = Join-Path $Path "REPORTE_ESTADISTICAS.md"
    Set-Content $ReportPath $ReportContent -Encoding UTF8
    
    Write-Log "✅ Reporte guardado en: $ReportPath"
}

function Remove-TempFiles {
    param($Path)
    
    Write-Log "🧹 Limpiando archivos temporales..."
    
    $TempPatterns = @("*.tmp", "*.temp", "*.bak", "*.backup", "*.old")
    $DeletedCount = 0
    
    foreach ($Pattern in $TempPatterns) {
        $TempFiles = Get-ChildItem -Path $Path -Recurse -Name $Pattern -Force -ErrorAction SilentlyContinue
        
        foreach ($File in $TempFiles) {
            try {
                $FilePath = Join-Path $Path $File
                Remove-Item $FilePath -Force
                $DeletedCount++
                Write-Log "🗑️  Eliminado: $File"
            } catch {
                Write-Log "⚠️  Error eliminando $File`: $($_.Exception.Message)" "WARN"
            }
        }
    }
    
    Write-Log "✅ $DeletedCount archivos temporales eliminados"
}

function Start-Maintenance {
    Write-Log "🚀 Iniciando mantenimiento automático..."
    Write-Log "=================================================="
    
    try {
        # Verificar que el directorio existe
        if (-not (Test-Path $BasePath)) {
            Write-Log "❌ Error: Directorio de documentos no encontrado: $BasePath" "ERROR"
            return $false
        }
        
        # 1. Escanear estructura
        $Stats = Get-FileStats -Path $BasePath
        
        # 2. Verificar integridad
        $IntegrityOK = Test-FileIntegrity -Path $BasePath
        
        # 3. Actualizar índices
        if ($UpdateIndexes) {
            Update-OrganizationStats -Path $BasePath -Stats $Stats
            Update-SearchIndex -Path $BasePath -Stats $Stats
        }
        
        # 4. Generar reporte
        if ($GenerateReport) {
            New-StatisticsReport -Path $BasePath -Stats $Stats
        }
        
        # 5. Limpiar archivos temporales
        if ($CleanTemp) {
            Remove-TempFiles -Path $BasePath
        }
        
        Write-Log "=================================================="
        Write-Log "✅ Mantenimiento automático completado exitosamente"
        
        return $true
        
    } catch {
        Write-Log "❌ Error durante el mantenimiento: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Función principal
function Main {
    Write-Host "🔧 Sistema de Mantenimiento Automático" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    
    if (Start-Maintenance) {
        Write-Host "`n🎉 ¡Mantenimiento completado exitosamente!" -ForegroundColor Green
        Write-Host "📊 Revisa el REPORTE_ESTADISTICAS.md para ver los detalles" -ForegroundColor Yellow
        Write-Host "📝 Log guardado en: $LogFile" -ForegroundColor Gray
    } else {
        Write-Host "`n💥 Error durante el mantenimiento" -ForegroundColor Red
        exit 1
    }
}

# Ejecutar función principal
Main






