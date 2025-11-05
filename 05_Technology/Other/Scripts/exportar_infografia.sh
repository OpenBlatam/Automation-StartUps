#!/bin/bash

echo "=========================================="
echo "EXPORTAR INFOGRAFÍA COMO JPEG"
echo "=========================================="
echo ""

# Check if HTML file exists
if [ ! -f "Infografia_Unidad-8_AdanPablo_semana4.html" ]; then
    echo "Error: No se encontró el archivo HTML de la infografía"
    exit 1
fi

echo "Archivo de infografía encontrado:"
ls -la Infografia_Unidad-8_AdanPablo_semana4.html

echo ""
echo "=========================================="
echo "INSTRUCCIONES PARA EXPORTAR COMO JPEG:"
echo "=========================================="
echo ""
echo "MÉTODO 1 - Captura de Pantalla (RECOMENDADO):"
echo "1. La infografía se ha abierto en tu navegador"
echo "2. Ajusta el zoom para que la infografía se vea completa"
echo "3. Usa la herramienta de captura de pantalla:"
echo "   - Mac: Cmd+Shift+4, selecciona el área de la infografía"
echo "   - Windows: Win+Shift+S, selecciona el área"
echo "4. Guarda la imagen como: Infografia_Unidad-8_AdanPablo_semana4.jpeg"
echo ""
echo "MÉTODO 2 - Herramientas de Navegador:"
echo "1. En el navegador, presiona F12 para abrir herramientas de desarrollador"
echo "2. Presiona Ctrl+Shift+P (Cmd+Option+P en Mac)"
echo "3. Busca 'screenshot' y selecciona 'Capture full size screenshot'"
echo "4. Guarda como: Infografia_Unidad-8_AdanPablo_semana4.jpeg"
echo ""
echo "MÉTODO 3 - Usando herramientas online:"
echo "1. Ve a html-css-js.com/html/html-to-image"
echo "2. Copia el contenido del archivo HTML"
echo "3. Pega en la herramienta y genera la imagen"
echo "4. Descarga como JPEG"
echo ""
echo "=========================================="
echo "REQUISITOS DEL ARCHIVO:"
echo "=========================================="
echo "✓ Formato: JPEG"
echo "✓ Nombre: Infografia_Unidad-8_AdanPablo_semana4.jpeg"
echo "✓ Contenido: Infografía completa de la Unidad 8"
echo "✓ Calidad: Alta resolución para buena legibilidad"
echo "=========================================="

# Try to take a screenshot using system tools
echo ""
echo "Intentando captura automática..."

# Check if we can use screencapture on Mac
if command -v screencapture &> /dev/null; then
    echo "Tomando captura de pantalla automática..."
    screencapture -x -t jpg Infografia_Unidad-8_AdanPablo_semana4.jpeg
    if [ -f "Infografia_Unidad-8_AdanPablo_semana4.jpeg" ]; then
        echo "✅ Captura automática exitosa!"
        echo "Archivo creado: Infografia_Unidad-8_AdanPablo_semana4.jpeg"
    else
        echo "❌ Captura automática falló. Usa los métodos manuales arriba."
    fi
else
    echo "❌ Herramienta de captura automática no disponible."
    echo "Usa los métodos manuales descritos arriba."
fi
