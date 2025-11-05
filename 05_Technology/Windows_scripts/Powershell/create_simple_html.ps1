# Script PowerShell simple para crear HTML del Curso Premium de IA en Marketing

Write-Host "🚀 Generando HTML del Curso Premium de IA en Marketing..." -ForegroundColor Green

# Rutas de archivos
$file1 = "AI_Marketing_Course_Complete_Structure.md"
$file2 = "AI_Marketing_Course_Resources_Delivery_Marketing_Feedback.md"
$outputFile = "Curso_Premium_IA_Marketing_Completo.html"

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

# Convertir Markdown básico a HTML
Write-Host "🎨 Convirtiendo a HTML..." -ForegroundColor Yellow

# Convertir títulos
$combinedContent = $combinedContent -replace '^# (.*?)$', '<h1>$1</h1>'
$combinedContent = $combinedContent -replace '^## (.*?)$', '<h2>$1</h2>'
$combinedContent = $combinedContent -replace '^### (.*?)$', '<h3>$1</h3>'
$combinedContent = $combinedContent -replace '^#### (.*?)$', '<h4>$1</h4>'
$combinedContent = $combinedContent -replace '^##### (.*?)$', '<h5>$1</h5>'
$combinedContent = $combinedContent -replace '^###### (.*?)$', '<h6>$1</h6>'

# Convertir negritas
$combinedContent = $combinedContent -replace '\*\*(.*?)\*\*', '<strong>$1</strong>'
$combinedContent = $combinedContent -replace '__(.*?)__', '<strong>$1</strong>'

# Convertir cursivas
$combinedContent = $combinedContent -replace '\*(.*?)\*', '<em>$1</em>'
$combinedContent = $combinedContent -replace '_(.*?)_', '<em>$1</em>'

# Convertir código
$combinedContent = $combinedContent -replace '`(.*?)`', '<code>$1</code>'

# Convertir separadores
$combinedContent = $combinedContent -replace '^---$', '<hr>'

# Crear documento HTML completo
Write-Host "📄 Creando documento HTML..." -ForegroundColor Yellow

$htmlContent = @"
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Curso Premium: Inteligencia Artificial Aplicada al Marketing</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
            font-size: 2.2em;
            text-align: center;
        }
        
        h1:first-child {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            border: none;
            margin: 0 0 30px 0;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 8px;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.8em;
        }
        
        h3 {
            color: #2980b9;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.4em;
        }
        
        h4 {
            color: #8e44ad;
            margin-top: 15px;
            margin-bottom: 8px;
            font-size: 1.2em;
        }
        
        h5, h6 {
            color: #27ae60;
            margin-top: 12px;
            margin-bottom: 6px;
        }
        
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        
        ul, ol {
            margin-bottom: 15px;
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        strong {
            color: #e74c3c;
            font-weight: bold;
        }
        
        em {
            color: #8e44ad;
            font-style: italic;
        }
        
        code {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            padding: 2px 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        hr {
            border: none;
            height: 2px;
            background-color: #3498db;
            margin: 30px 0;
        }
        
        @media print {
            body {
                background-color: white;
            }
            
            .container {
                box-shadow: none;
                padding: 0;
            }
            
            h1 {
                page-break-before: always;
            }
            
            h1:first-child {
                page-break-before: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        $combinedContent
    </div>
</body>
</html>
"@

# Guardar archivo HTML
Write-Host "💾 Guardando archivo HTML..." -ForegroundColor Yellow
$htmlContent | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "✅ HTML generado exitosamente: $outputFile" -ForegroundColor Green

$fileSize = (Get-Item $outputFile).Length / 1MB
Write-Host "📊 Tamaño del archivo: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan

Write-Host "`n📋 Para convertir a PDF:" -ForegroundColor Yellow
Write-Host "1. Abre el archivo HTML en tu navegador" -ForegroundColor White
Write-Host "2. Presiona Ctrl+P (Cmd+P en Mac)" -ForegroundColor White
Write-Host "3. Selecciona 'Guardar como PDF'" -ForegroundColor White
Write-Host "4. Ajusta la configuración de impresión si es necesario" -ForegroundColor White

Write-Host "`n🎉 ¡HTML del curso generado exitosamente!" -ForegroundColor Green
Write-Host "📧 El archivo está listo para convertir a PDF desde el navegador." -ForegroundColor Green
