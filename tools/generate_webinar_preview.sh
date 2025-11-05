#!/bin/bash
# Script para generar previews HTML de todos los SVGs de webinar
# Uso: ./tools/generate_webinar_preview.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/exports/webinar-previews"
PREVIEW_HTML="$OUTPUT_DIR/index.html"

mkdir -p "$OUTPUT_DIR"

# Buscar todos los SVGs de webinar
SVG_FILES=$(find "$PROJECT_ROOT" -maxdepth 1 -name "webinar-*.svg" | sort)

# Generar HTML
cat > "$PREVIEW_HTML" << 'HTMLHEAD'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webinar Ad Previews</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, sans-serif;
            background: linear-gradient(135deg, #0B1229 0%, #10314A 100%);
            color: #FFFFFF;
            padding: 40px 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            font-size: 48px;
            margin-bottom: 20px;
            text-align: center;
            background: linear-gradient(135deg, #00E5A8 0%, #00B4D8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stats {
            text-align: center;
            margin-bottom: 40px;
            opacity: 0.8;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 40px;
            margin-top: 40px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 229, 168, 0.2);
            border-color: rgba(0, 229, 168, 0.3);
        }
        .card-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 16px;
            color: #00E5A8;
        }
        .card-preview {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            overflow: hidden;
        }
        .card-preview svg {
            width: 100%;
            height: auto;
            display: block;
            border-radius: 8px;
        }
        .card-info {
            font-size: 14px;
            opacity: 0.7;
            line-height: 1.6;
        }
        .dimensions {
            display: inline-block;
            background: rgba(0, 229, 168, 0.2);
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            margin-top: 8px;
        }
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            h1 {
                font-size: 32px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Webinar Ad Previews</h1>
        <div class="stats" id="stats"></div>
        <div class="grid" id="grid"></div>
    </div>
    <script>
HTMLHEAD

# Contar archivos
SVG_COUNT=$(echo "$SVG_FILES" | wc -l | tr -d ' ')

echo "        const statsEl = document.getElementById('stats');" >> "$PREVIEW_HTML"
echo "        statsEl.innerHTML = '<p>📊 Total: <strong>$SVG_COUNT</strong> variantes</p>';" >> "$PREVIEW_HTML"
echo "        const gridEl = document.getElementById('grid');" >> "$PREVIEW_HTML"

# Generar cards para cada SVG
while IFS= read -r svg_file; do
    if [ -f "$svg_file" ]; then
        filename=$(basename "$svg_file")
        # Extraer dimensiones del SVG
        dimensions=$(grep -oE 'width="[0-9]+" height="[0-9]+"' "$svg_file" | head -1 || echo 'width="1920" height="1080"')
        width=$(echo "$dimensions" | grep -oE 'width="[0-9]+"' | grep -oE '[0-9]+')
        height=$(echo "$dimensions" | grep -oE 'height="[0-9]+"' | grep -oE '[0-9]+')
        
        # Leer contenido del SVG (escapado para JS)
        svg_content=$(cat "$svg_file" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | tr '\n' ' ')
        
        echo "        (() => {" >> "$PREVIEW_HTML"
        echo "            const card = document.createElement('div');" >> "$PREVIEW_HTML"
        echo "            card.className = 'card';" >> "$PREVIEW_HTML"
        echo "            card.innerHTML = \`" >> "$PREVIEW_HTML"
        echo "                <div class=\"card-title\">${filename}</div>" >> "$PREVIEW_HTML"
        echo "                <div class=\"card-preview\">${svg_content}</div>" >> "$PREVIEW_HTML"
        echo "                <div class=\"card-info\">" >> "$PREVIEW_HTML"
        echo "                    <div class=\"dimensions\">${width}×${height}px</div>" >> "$PREVIEW_HTML"
        echo "                </div>" >> "$PREVIEW_HTML"
        echo "            \`;" >> "$PREVIEW_HTML"
        echo "            gridEl.appendChild(card);" >> "$PREVIEW_HTML"
        echo "        })();" >> "$PREVIEW_HTML"
    fi
done <<< "$SVG_FILES"

cat >> "$PREVIEW_HTML" << 'HTMLFOOT'
    </script>
</body>
</html>
HTMLFOOT

echo "✅ Preview generado en: $PREVIEW_HTML"
echo "📊 Total de archivos: $SVG_COUNT"

