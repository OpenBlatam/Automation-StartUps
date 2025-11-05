# Script PowerShell para crear documento RTF del Curso Premium de IA en Marketing

Write-Host "🚀 Generando documento RTF del Curso Premium de IA en Marketing..." -ForegroundColor Green

# Rutas de archivos
$file1 = "AI_Marketing_Course_Complete_Structure.md"
$file2 = "AI_Marketing_Course_Resources_Delivery_Marketing_Feedback.md"
$outputFile = "Curso_Premium_IA_Marketing_Completo.rtf"

# Verificar que los archivos existen
if (-not (Test-Path $file1)) {
    Write-Host "❌ Error: No se encontró $file1" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $file2)) {
    Write-Host "❌ Error: No se encontró $file2" -ForegroundColor Red
    exit 1
}

Write-Host "📖 Leyendo archivos Markdown..." -ForegroundColor Yellow

# Leer contenido de ambos archivos
$content1 = Get-Content $file1 -Raw -Encoding UTF8
$content2 = Get-Content $file2 -Raw -Encoding UTF8

# Combinar contenido
Write-Host "🔗 Combinando contenido..." -ForegroundColor Yellow
$combinedContent = $content1 + "`n`n" + $content2

# Convertir Markdown básico a RTF
Write-Host "🎨 Convirtiendo a RTF..." -ForegroundColor Yellow

# Convertir títulos
$combinedContent = $combinedContent -replace '^# (.*?)$', "`n\\par\\b\\fs28\\cf2 `$1\\b0\\fs24\\par`n"
$combinedContent = $combinedContent -replace '^## (.*?)$', "`n\\par\\b\\fs24\\cf3 `$1\\b0\\fs20\\par`n"
$combinedContent = $combinedContent -replace '^### (.*?)$', "`n\\par\\b\\fs20\\cf4 `$1\\b0\\fs18\\par`n"
$combinedContent = $combinedContent -replace '^#### (.*?)$', "`n\\par\\b\\fs18\\cf5 `$1\\b0\\fs16\\par`n"
$combinedContent = $combinedContent -replace '^##### (.*?)$', "`n\\par\\b\\fs16\\cf6 `$1\\b0\\fs14\\par`n"
$combinedContent = $combinedContent -replace '^###### (.*?)$', "`n\\par\\b\\fs14\\cf7 `$1\\b0\\fs12\\par`n"

# Convertir negritas
$combinedContent = $combinedContent -replace '\*\*(.*?)\*\*', '\\b $1\\b0'
$combinedContent = $combinedContent -replace '__(.*?)__', '\\b $1\\b0'

# Convertir cursivas
$combinedContent = $combinedContent -replace '\*(.*?)\*', '\\i $1\\i0'
$combinedContent = $combinedContent -replace '_(.*?)_', '\\i $1\\i0'

# Convertir código
$combinedContent = $combinedContent -replace '`(.*?)`', '\\f1 $1\\f0'

# Convertir separadores
$combinedContent = $combinedContent -replace '^---$', "`n\\par\\par\\line\\par\\par`n"

# Convertir listas básicas
$lines = $combinedContent -split "`n"
$resultLines = @()

foreach ($line in $lines) {
    if ($line.Trim().StartsWith('- ') -or $line.Trim().StartsWith('* ')) {
        $content = $line.Trim().Substring(2).Trim()
        $resultLines += "\\par\\bullet $content"
    } elseif ($line.Trim() -match '^\d+\. ') {
        $content = $line.Trim().Substring(3).Trim()
        $resultLines += "\\par\\tab $content"
    } else {
        if ($line.Trim()) {
            $resultLines += "\\par $line"
        } else {
            $resultLines += "\\par"
        }
    }
}

$rtfContent = $resultLines -join ""

# Crear documento RTF completo
Write-Host "📄 Creando documento RTF..." -ForegroundColor Yellow

$rtfDocument = @"
{\rtf1\ansi\deff0
{\fonttbl{\f0\fswiss\fcharset0 Calibri;}{\f1\fmodern\fcharset0 Courier New;}}
{\colortbl;\red0\green0\blue0;\red44\green62\blue80;\red52\green73\blue94;\red41\green128\blue185;\red142\green68\blue173;\red39\green174\blue96;\red231\green76\blue60;}
{\stylesheet{\s0\snext0\sb240\sa120\ql\f0\fs24 Normal;}}

\pard\qc\b\fs32\cf2 🚀 CURSO PREMIUM: INTELIGENCIA ARTIFICIAL APLICADA AL MARKETING\b0\fs24\par
\pard\qc\b\fs20\cf3 Programa de Certificación Profesional Avanzado\b0\fs18\par
\pard\qc\b\fs18\cf4 Transforma tu Carrera con IA: De Principiante a Experto en 8 Semanas\b0\fs16\par

\pard\ql\b\fs16\cf2 📋 INFORMACIÓN DEL CURSO\b0\fs14\par
\pard\ql\bullet 8 Módulos Principales + 12 Módulos Especializados Opcionales\par
\pard\ql\bullet 100+ Herramientas de IA premium incluidas\par
\pard\ql\bullet 50+ Casos de Estudio reales por industria\par
\pard\ql\bullet 5 Especializaciones por industria\par
\pard\ql\bullet Certificaciones verificables en blockchain\par
\pard\ql\bullet Valor total: $15,000+ en herramientas y recursos\par
\pard\ql\bullet Precio del curso: $497 (97% de descuento)\par

\pard\ql\par\par\line\par\par

$rtfContent

\pard\ql\par\par\line\par\par

\pard\qc\i\fs12 © 2024 - Blatam AI Marketing. Todos los derechos reservados.\i0\par
}
"@

# Guardar archivo RTF
Write-Host "💾 Guardando archivo RTF..." -ForegroundColor Yellow
$rtfDocument | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "✅ Documento RTF generado exitosamente: $outputFile" -ForegroundColor Green

$fileSize = (Get-Item $outputFile).Length / 1MB
Write-Host "📊 Tamaño del archivo: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan

Write-Host "`n📋 Para abrir el documento:" -ForegroundColor Yellow
Write-Host "1. Haz doble clic en el archivo .rtf" -ForegroundColor White
Write-Host "2. Se abrirá automáticamente en Microsoft Word" -ForegroundColor White
Write-Host "3. También es compatible con Google Docs y LibreOffice" -ForegroundColor White

Write-Host "`n🎉 ¡Documento RTF generado exitosamente!" -ForegroundColor Green
Write-Host "📧 El archivo se puede abrir directamente en Microsoft Word." -ForegroundColor Green
