#!/usr/bin/env bash
# Benchmarking de rendimiento: mide tiempos de ejecución de scripts

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BENCHMARK_FILE="$ROOT_DIR/exports/benchmark_$(date +%Y%m%d_%H%M%S).json"

echo "⚡ Benchmark de Rendimiento"
echo "=========================="
echo ""

declare -A TIMES
declare -A RESULTS

# Función para medir tiempo de ejecución
benchmark_cmd() {
  local name="$1"
  local cmd="$2"
  local start=$(date +%s.%N)
  
  if eval "$cmd" > /dev/null 2>&1; then
    local end=$(date +%s.%N)
    local duration=$(echo "$end - $start" | bc)
    TIMES["$name"]="$duration"
    RESULTS["$name"]="success"
    echo "✅ $name: ${duration}s"
  else
    TIMES["$name"]="0"
    RESULTS["$name"]="failed"
    echo "❌ $name: falló"
  fi
}

echo "Ejecutando benchmarks..."
echo ""

# Benchmarks
benchmark_cmd "Health Check" "bash tools/health_check.sh"
benchmark_cmd "Quick Audit" "bash tools/quick_audit.sh"
benchmark_cmd "SVG Integrity" "bash tools/validate_svg_integrity.sh"
benchmark_cmd "Check Dimensions" "bash tools/check_dimensions.sh"
benchmark_cmd "Check Tokens" "node tools/check_token_coverage.js"
benchmark_cmd "Apply Tokens" "node tools/apply_tokens.js"
benchmark_cmd "Smart Recommendations" "node tools/smart_recommendations.js"

# Generar JSON
echo ""
echo "Generando reporte JSON..."

json="{"
json+="\"timestamp\":\"$(date -Iseconds)\","
json+="\"benchmarks\":{"

first=true
for key in "${!TIMES[@]}"; do
  if [ "$first" = false ]; then
    json+=","
  fi
  json+="\"$key\":{"
  json+="\"duration\":${TIMES[$key]},"
  json+="\"status\":\"${RESULTS[$key]}\""
  json+="}"
  first=false
done

json+="},"
json+="\"summary\":{"
json+="\"total_tests\":${#TIMES[@]},"
json+="\"passed\":$(printf '%s\n' "${RESULTS[@]}" | grep -c success || echo 0),"
json+="\"failed\":$(printf '%s\n' "${RESULTS[@]}" | grep -c failed || echo 0),"
json+="\"total_duration\":$(IFS=+; echo "${TIMES[*]}" | bc)"
json+="}"
json+="}"

mkdir -p "$(dirname "$BENCHMARK_FILE")"
echo "$json" | jq '.' > "$BENCHMARK_FILE" 2>/dev/null || echo "$json" > "$BENCHMARK_FILE"

echo "✅ Benchmark guardado: $BENCHMARK_FILE"

# Mostrar resumen
echo ""
echo "📊 Resumen:"
TOTAL_TIME=$(IFS=+; echo "${TIMES[*]}" | bc)
PASSED=$(printf '%s\n' "${RESULTS[@]}" | grep -c success || echo 0)
FAILED=$(printf '%s\n' "${RESULTS[@]}" | grep -c failed || echo 0)

echo "  Tiempo total: ${TOTAL_TIME}s"
echo "  ✅ Exitosos: $PASSED"
echo "  ❌ Fallidos: $FAILED"

