#!/usr/bin/env bash
set -euo pipefail

# docs_stats.sh - Mide tamaño, palabras y tiempo de lectura estimado

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "Archivo,Bytes,Palabras,MinLectura"
for f in *.md; do
  bytes=$(wc -c < "$f" | tr -d ' ')
  words=$(wc -w < "$f" | tr -d ' ')
  # 200 palabras/min aprox.
  mins=$(( (words + 199) / 200 ))
  echo "${f},${bytes},${words},${mins}"
done


