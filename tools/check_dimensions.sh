#!/usr/bin/env bash
# Verifica que todos los SVG tengan dimensiones correctas según su categoría

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$ROOT_DIR/exports/dimensions_report.txt"

echo "📐 Verificando dimensiones de SVG..." > "$REPORT"
echo "Fecha: $(date)" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "" >> "$REPORT"

# Definir dimensiones esperadas por patrón
declare -A EXPECTED_DIMENSIONS=(
  ["1080x1080"]="1080 1080"
  ["1080x1350"]="1080 1350"
  ["1080x1920"]="1080 1920"
  ["1200x627"]="1200 627"
)

declare -A DIMENSION_PATTERNS=(
  ["1080x1080"]="design/instagram/1080x1080|design/instagram/highlights|design/instagram/reels/cover_1080x1920|design/webinars.*square"
  ["1080x1350"]="design/instagram/1080x1350"
  ["1080x1920"]="design/instagram/1080x1920|design/instagram/reels|ads/linkedin.*1080x1920|design/webinars.*vertical|design/webinars/prerolls"
  ["1200x627"]="ads/linkedin.*1200x627"
)

ISSUES=0

for dim_key in "${!DIMENSION_PATTERNS[@]}"; do
  pattern="${DIMENSION_PATTERNS[$dim_key]}"
  expected="${EXPECTED_DIMENSIONS[$dim_key]}"
  expected_w="${expected%% *}"
  expected_h="${expected##* }"
  
  echo "Verificando $dim_key ($expected_w×$expected_h)..." >> "$REPORT"
  echo "Patrón: $pattern" >> "$REPORT"
  
  find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
    rel_path="${svg#$ROOT_DIR/}"
    
    # Verificar si coincide con el patrón
    if ! echo "$rel_path" | grep -qE "$pattern"; then
      continue
    fi
    
    # Extraer viewBox o width/height
    if grep -q "viewBox" "$svg" 2>/dev/null; then
      viewbox=$(grep -o 'viewBox="[^"]*"' "$svg" | head -1 | cut -d'"' -f2)
      if [ -n "$viewbox" ]; then
        w=$(echo "$viewbox" | awk '{print $3}')
        h=$(echo "$viewbox" | awk '{print $4}')
        
        # Comparar (permitir pequeñas diferencias por redondeo)
        if [ -n "$w" ] && [ -n "$h" ]; then
          w_int=${w%.*}
          h_int=${h%.*}
          if [ "$w_int" != "$expected_w" ] || [ "$h_int" != "$expected_h" ]; then
            echo "  ⚠️  $rel_path: viewBox tiene $w×$h (esperado: $expected_w×$expected_h)" >> "$REPORT"
            ((ISSUES++))
          fi
        fi
      fi
    elif grep -qE 'width="[0-9]+"|height="[0-9]+"' "$svg" 2>/dev/null; then
      width=$(grep -oE 'width="([0-9]+)"' "$svg" | head -1 | cut -d'"' -f2)
      height=$(grep -oE 'height="([0-9]+)"' "$svg" | head -1 | cut -d'"' -f2)
      
      if [ -n "$width" ] && [ -n "$height" ]; then
        if [ "$width" != "$expected_w" ] || [ "$height" != "$expected_h" ]; then
          echo "  ⚠️  $rel_path: dimensiones $width×$height (esperado: $expected_w×$expected_h)" >> "$REPORT"
          ((ISSUES++))
        fi
      fi
    else
      echo "  ⚠️  $rel_path: sin dimensiones definidas" >> "$REPORT"
      ((ISSUES++))
    fi
  done
  
  echo "" >> "$REPORT"
done

echo "=================================" >> "$REPORT"
if [ $ISSUES -eq 0 ]; then
  echo "✅ Todas las dimensiones son correctas" >> "$REPORT"
else
  echo "⚠️  Se encontraron $ISSUES problema(s) de dimensiones" >> "$REPORT"
fi

echo ""
echo "Reporte guardado en: $REPORT"
cat "$REPORT"


