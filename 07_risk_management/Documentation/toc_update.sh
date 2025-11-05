#!/usr/bin/env bash
set -euo pipefail

# toc_update.sh - Genera/actualiza TOC entre marcadores:
# <!-- TOC START --> y <!-- TOC END --> en cada .md (no destructivo sin marcador)
# Uso: ./toc_update.sh [--apply]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

slugify() {
  tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9\s-]//g; s/[[:space:]]+/-/g; s/-+/-/g; s/^-|-$//g'
}

gen_toc() {
  local file="$1"
  # headings con niveles y slugs
  awk '
    /^#{1,6} / {
      level=length($1);
      $1=""; sub(/^ /,"");
      title=$0;
      print level "\t" title;
    }
  ' "$file" | while IFS=$'\t' read -r level title; do
    slug=$(printf '%s' "$title" | slugify)
    indent=""; for ((i=2;i<=level;i++)); do indent="$indent  "; done
    printf "%s- [%s](#%s)\n" "$indent" "$title" "$slug"
  done
}

mapfile -t MD_FILES < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

changed=0
for f in "${MD_FILES[@]}"; do
  if ! grep -q "<!-- TOC START -->" "$f"; then
    continue
  fi
  toc="$(gen_toc "$f")"
  newc=$(awk -v TOC="$toc" '
    BEGIN{in_toc=0}
    {
      if($0 ~ /<!-- TOC START -->/){
        print $0; print ""; print TOC; in_toc=1; next
      }
      if(in_toc==1 && $0 ~ /<!-- TOC END -->/){ in_toc=0 }
      if(in_toc==0){ print $0 }
    }
  ' "$f")
  if [[ $APPLY -eq 1 ]]; then
    printf "%s" "$newc" > "$f"
  fi
  changed=1
  echo "[toc] Actualizado: $(basename "$f")"
done

if [[ $changed -eq 0 ]]; then
  echo "[toc] No se encontraron marcadores TOC"
fi


