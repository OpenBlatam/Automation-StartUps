#!/usr/bin/env bash
set -euo pipefail

# publish_site.sh - Genera un sitio estático simple en ./site desde los .md
# Requiere pandoc para conversión rica; si no está, genera HTML mínimo

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_DIR="$ROOT_DIR/site"
mkdir -p "$SITE_DIR"

header_html() {
  cat <<'HTML'
<!doctype html>
<html lang="es"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css"/>
<title>Documentation</title></head><body>
HTML
}

footer_html() {
  cat <<'HTML'
</body></html>
HTML
}

build_with_pandoc() {
  for f in "$ROOT_DIR"/*.md; do
    name="$(basename "$f" .md)"
    pandoc "$f" -s -M lang=es -c https://cdn.jsdelivr.net/npm/water.css@2/out/water.css -o "$SITE_DIR/${name}.html" || true
  done
}

build_minimal() {
  for f in "$ROOT_DIR"/*.md; do
    name="$(basename "$f" .md)"
    header_html > "$SITE_DIR/${name}.html"
    echo "<pre>" >> "$SITE_DIR/${name}.html"
    sed -e 's/&/&amp;/g;s/</\&lt;/g;s/>/\&gt;/g' "$f" >> "$SITE_DIR/${name}.html"
    echo "</pre>" >> "$SITE_DIR/${name}.html"
    footer_html >> "$SITE_DIR/${name}.html"
  done
}

echo "[site] Generando HTML en $SITE_DIR"
if command -v pandoc >/dev/null 2>&1; then
  build_with_pandoc
else
  echo "[site] pandoc no disponible; usando render mínimo" >&2
  build_minimal
fi

# Índice
INDEX="$SITE_DIR/index.html"
header_html > "$INDEX"
echo "<h1>Documentación</h1>" >> "$INDEX"
echo "<ul>" >> "$INDEX"
for h in "$SITE_DIR"/*.html; do
  base="$(basename "$h")"
  [[ "$base" == "index.html" ]] && continue
  echo "  <li><a href=\"$base\">$base</a></li>" >> "$INDEX"
done
echo "</ul>" >> "$INDEX"
footer_html >> "$INDEX"

echo "[site] Sitio generado en $SITE_DIR"


