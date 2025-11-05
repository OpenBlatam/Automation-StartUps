#!/bin/bash
# Rellena placeholders en todos los SVGs webinar-*.svg (in-place)
# Uso:
#   ./tools/fill_placeholders.sh "15 Nov 2024" "18:00" "https://tu-dominio.com/webinar?utm_source=youtube&utm_medium=preroll&utm_campaign=campana&utm_content=contenido" "TU LOGO"
#       FECHA                HORA     URL                                                                          LOGO_TEXT
# Flags:
#   --dry-run  Muestra cambios sin escribir
#   --scoped PATTERN  Limita a archivos que coinciden (default: webinar-*.svg)

set -euo pipefail

DRY_RUN=false
SCOPE_PATTERN="webinar-*.svg"

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true; shift ;;
    --scoped)
      SCOPE_PATTERN="$2"; shift 2 ;;
    --)
      shift; break ;;
    -*|--*)
      echo "Flag no reconocido: $1" >&2; exit 1 ;;
    *)
      break ;;
  esac
done

if [[ $# -lt 4 ]]; then
  echo "Uso: $0 [--dry-run] [--scoped PATTERN] FECHA HORA URL LOGO_TEXT" >&2
  exit 1
fi

FECHA="$1"; HORA="$2"; URL="$3"; LOGO_TEXT="$4"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Mac (BSD sed) compatible in-place edit
_sed() {
  local expr="$1"; shift
  if $DRY_RUN; then
    sed -E "$expr" "$@" | diff -u "$@" - || true
  else
    sed -E -i '' "$expr" "$@"
  fi
}

FILES=( $(find "$ROOT_DIR" -maxdepth 1 -name "$SCOPE_PATTERN" | sort) )
if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No se encontraron archivos que coincidan con '$SCOPE_PATTERN'" >&2
  exit 1
fi

echo "Procesando ${#FILES[@]} archivos... (scope: $SCOPE_PATTERN)"

# Reemplazos principales
for f in "${FILES[@]}"; do
  _sed "s/\[FECHA\]/$(printf '%s' "$FECHA" | sed 's/[\&/]/\\&/g')/g" "$f"
  _sed "s/\[HORA\]/$(printf '%s' "$HORA" | sed 's/[\&/]/\\&/g')/g" "$f"
  _sed "s#\[URL\]#$(printf '%s' "$URL" | sed 's#[\&/]#\\&#g')#g" "$f"
  _sed "s/TU LOGO/$(printf '%s' "$LOGO_TEXT" | sed 's/[\&/]/\\&/g')/g" "$f"
  # Opcionales si existen
  _sed "s/\[SPEAKER\]/Ponente Invitado/g" "$f" || true
  _sed "s/\[CARGO\]/Head of Growth/g" "$f" || true
  _sed "s/\[EMPRESA\]/Tu Empresa/g" "$f" || true
  _sed "s/\[COUNTDOWN\]/Empieza pronto/g" "$f" || true
  # Zona (si aparece en texto)
  _sed "s/\(GMT-\)[0-9]+/GMT-5/g" "$f" || true
  echo "✓ $(basename "$f")"
done

echo "Listo."

