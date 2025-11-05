#!/usr/bin/env bash
set -euo pipefail

# enforce_yaml_keys.sh - Asegura claves mínimas en front matter: title, category, created, path
# Uso: ./enforce_yaml_keys.sh [--apply]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

today=$(date +%Y-%m-%d)

ensure_frontmatter() {
  local f="$1"
  local content
  content=$(cat "$f")
  if [[ $content != ---$'\n'* ]]; then
    # insertar bloque
    local base title path
    base=$(basename "$f")
    title="${base%.md}"
    path="07_risk_management/documentation/${base,,}"
    printf "---\n" > "$f.tmp"
    printf "title: \"%s\"\n" "$title" >> "$f.tmp"
    printf "category: \"07_risk_management\"\n" >> "$f.tmp"
    printf "tags: []\n" >> "$f.tmp"
    printf "created: \"%s\"\n" "$today" >> "$f.tmp"
    printf "path: \"%s\"\n" "$path" >> "$f.tmp"
    printf "---\n\n" >> "$f.tmp"
    cat "$f" >> "$f.tmp"
    mv "$f.tmp" "$f"
    echo "[enforce-yaml] añadido front matter en $(basename "$f")"
    return
  fi
  # ya tiene front matter; asegurar claves
  awk -v TODAY="$today" -v FILEBASE="$(basename "$f")" '
    BEGIN{in=0; seen_t=0; seen_c=0; seen_cr=0; seen_p=0}
    /^---$/ { if(in==0){in=1; print; next} else { # cierre
        if(seen_t==0){ printf("title: \"%s\"\n", FILEBASE); }
        if(seen_c==0){ print "category: \"07_risk_management\""; }
        if(seen_cr==0){ printf("created: \"%s\"\n", TODAY); }
        if(seen_p==0){ printf("path: \"07_risk_management/documentation/%s\"\n", tolower(FILEBASE)); }
        print; in=0; next }
    }
    { if(in==1){
        if($0 ~ /^title:/) seen_t=1;
        if($0 ~ /^category:/) seen_c=1;
        if($0 ~ /^created:/) seen_cr=1;
        if($0 ~ /^path:/) seen_p=1;
      }
      print
    }
  ' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
}

for f in "$ROOT_DIR"/*.md; do
  if [[ $APPLY -eq 1 ]]; then
    ensure_frontmatter "$f"
  else
    # modo validación: solo informar faltantes
    block=$(awk 'found==0 && /^---$/ {found=1; next} found==1 && /^---$/ {exit} found==1 {print}' "$f")
    for key in title category created path; do
      if ! printf '%s\n' "$block" | grep -q "^$key:"; then
        echo "[enforce-yaml] falta $key en $(basename "$f")" >&2
      fi
    done
  fi
done

echo "[enforce-yaml] OK"


