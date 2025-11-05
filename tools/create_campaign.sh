#!/bin/bash
# Crea una campaña: copia SVGs a exports/campaigns/<slug> y rellena placeholders
# Uso:
#   ./tools/create_campaign.sh --slug nov-2024 --fecha "15 Nov 2024" --hora "18:00" \
#     --url "https://tu-dominio.com/webinar?utm_source=youtube&utm_medium=preroll&utm_campaign=nov2024&utm_content=youtube" \
#     --logo "TU MARCA"
# Flags opcionales:
#   --scope PATTERN   (default: webinar-*.svg)

set -euo pipefail

SLUG=""; FECHA=""; HORA=""; URL=""; LOGO=""; SCOPE="webinar-*.svg"

# Parse
while [[ $# -gt 0 ]]; do
  case "$1" in
    --slug) SLUG="$2"; shift 2 ;;
    --fecha) FECHA="$2"; shift 2 ;;
    --hora) HORA="$2"; shift 2 ;;
    --url) URL="$2"; shift 2 ;;
    --logo) LOGO="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    *) echo "Flag no reconocido: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$SLUG" || -z "$FECHA" || -z "$HORA" || -z "$URL" || -z "$LOGO" ]]; then
  echo "Uso: $0 --slug SLUG --fecha FECHA --hora HORA --url URL --logo LOGO [--scope PATTERN]" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EXPORT_DIR="$ROOT_DIR/exports/campaigns/$SLUG"
mkdir -p "$EXPORT_DIR"

echo "Copiando SVGs ($SCOPE) a $EXPORT_DIR ..."
find "$ROOT_DIR" -maxdepth 1 -name "$SCOPE" -print -exec cp {} "$EXPORT_DIR" \;

pushd "$EXPORT_DIR" >/dev/null

echo "Rellenando placeholders..."
"$ROOT_DIR/tools/fill_placeholders.sh" "$FECHA" "$HORA" "$URL" "$LOGO" --scoped "*.svg"

cat > "$EXPORT_DIR/README.txt" <<EOF
Campaña: $SLUG
Fecha: $FECHA
Hora: $HORA
URL: $URL
Logo: $LOGO
Archivos: $(ls -1 *.svg | wc -l)
EOF

popd >/dev/null

echo "Listo: $EXPORT_DIR"

