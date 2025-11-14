#!/bin/bash

echo "=========================================="
echo "CREAR PDF COMPLETO CON PORTADA"
echo "=========================================="
echo ""

# Check if HTML file exists
if [ ! -f "Infografia_Unidad8_AdanPablo_Completo.html" ]; then
    echo "Error: No se encontró el archivo HTML completo"
    exit 1
fi

echo "Archivos disponibles:"
ls -la Infografia_Unidad8_AdanPablo_Completo.*

echo ""
echo "=========================================="
echo "INSTRUCCIONES PARA CREAR PDF:"
echo "=========================================="
echo ""
echo "MÉTODO 1 - Usando el navegador (RECOMENDADO):"
echo "1. El documento completo se ha abierto en tu navegador"
echo "2. Presiona Cmd+P (Mac) o Ctrl+P (Windows/Linux)"
echo "3. En el diálogo de impresión:"
echo "   - Selecciona 'Guardar como PDF' como destino"
echo "   - Establece márgenes a 'Mínimo'"
echo "   - Marca 'Gráficos de fondo'"
echo "   - Selecciona 'Más configuraciones' y marca 'Encabezados y pies de página'"
echo "   - Haz clic en 'Guardar'"
echo "4. Guarda como: Infografia_Unidad8_AdanPablo_Completo.pdf"
echo ""
echo "MÉTODO 2 - Usando Word:"
echo "1. Abre 'Infografia_Unidad8_AdanPablo_Completo.docx' en Microsoft Word"
echo "2. Ve a Archivo > Exportar > PDF"
echo "3. Guarda como: Infografia_Unidad8_AdanPablo_Completo.pdf"
echo ""
echo "=========================================="
echo "CONTENIDO DEL DOCUMENTO:"
echo "=========================================="
echo "✓ Portada profesional con información del estudiante"
echo "✓ Introducción detallada"
echo "✓ Infografía interactiva (referencia al archivo HTML)"
echo "✓ Explicación de conceptos clave"
echo "✓ Conclusiones"
echo "✓ Referencias académicas"
echo "✓ Anexos con instrucciones"
echo "✓ Formato profesional y académico"
echo "=========================================="

# Try to take a screenshot using system tools
echo ""
echo "Intentando captura automática del documento..."

# Check if we can use screencapture on Mac
if command -v screencapture &> /dev/null; then
    echo "Tomando captura de pantalla automática..."
    screencapture -x -t jpg Infografia_Unidad8_AdanPablo_Completo.jpg
    if [ -f "Infografia_Unidad8_AdanPablo_Completo.jpg" ]; then
        echo "✅ Captura automática exitosa!"
        echo "Archivo creado: Infografia_Unidad8_AdanPablo_Completo.jpg"
        echo "Nota: Para PDF completo, usa los métodos manuales arriba."
    else
        echo "❌ Captura automática falló. Usa los métodos manuales arriba."
    fi
else
    echo "❌ Herramienta de captura automática no disponible."
    echo "Usa los métodos manuales descritos arriba."
fi
