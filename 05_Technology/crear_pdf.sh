#!/bin/bash

echo "=========================================="
echo "CREANDO PDF DEL ENTREGABLE 2 - SEMANA 4"
echo "=========================================="
echo ""

# Check if HTML file exists
if [ ! -f "Entregable2_Semana4_AdanPablo.html" ]; then
    echo "Error: No se encontró el archivo HTML"
    exit 1
fi

echo "Archivos disponibles:"
ls -la Entregable2_Semana4_AdanPablo.*

echo ""
echo "=========================================="
echo "INSTRUCCIONES PARA CREAR EL PDF:"
echo "=========================================="
echo ""
echo "MÉTODO 1 - Usando el navegador (RECOMENDADO):"
echo "1. Abre el archivo 'Entregable2_Semana4_AdanPablo.html' en tu navegador"
echo "2. Presiona Cmd+P (Mac) o Ctrl+P (Windows/Linux)"
echo "3. En el diálogo de impresión:"
echo "   - Selecciona 'Guardar como PDF' como destino"
echo "   - Establece márgenes a 'Mínimo'"
echo "   - Marca 'Gráficos de fondo'"
echo "   - Haz clic en 'Guardar'"
echo "4. Guarda como 'Entregable2_Semana4_AdanPablo.pdf'"
echo ""
echo "MÉTODO 2 - Usando Word/Pages:"
echo "1. Abre 'Entregable2_Semana4_AdanPablo.docx' en Microsoft Word o Pages"
echo "2. Ve a Archivo > Exportar > PDF"
echo "3. Guarda como 'Entregable2_Semana4_AdanPablo.pdf'"
echo ""
echo "=========================================="

# Try to open the HTML file in the default browser
echo "Abriendo archivo HTML en el navegador..."
open "Entregable2_Semana4_AdanPablo.html"

echo ""
echo "El archivo HTML se ha abierto en tu navegador."
echo "Sigue las instrucciones del MÉTODO 1 para crear el PDF."
