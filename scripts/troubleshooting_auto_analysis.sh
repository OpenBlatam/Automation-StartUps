#!/bin/bash
# Script de Análisis Automático de Troubleshooting
# Ejecuta análisis periódicos y genera reportes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="${PROJECT_ROOT}/reports/troubleshooting"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
DB_URL="${DATABASE_URL:-postgresql://user:pass@localhost:5432/dbname}"
DAYS="${ANALYSIS_DAYS:-30}"

# Crear directorio de reportes
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}🔍 Análisis Automático de Troubleshooting${NC}"
echo "Fecha: $(date)"
echo "Período: últimos $DAYS días"
echo ""

# 1. Análisis de Tendencias
echo -e "${GREEN}1. Analizando tendencias...${NC}"
python3 "$SCRIPT_DIR/troubleshooting_analyzer.py" \
  --db-url "$DB_URL" \
  --command trends \
  --days "$DAYS" \
  --group-by day \
  --output "$OUTPUT_DIR/trends_${TIMESTAMP}.json" || echo "⚠️ Error en análisis de tendencias"

# 2. Identificar Mejoras
echo -e "${GREEN}2. Identificando problemas que necesitan mejora...${NC}"
python3 "$SCRIPT_DIR/troubleshooting_analyzer.py" \
  --db-url "$DB_URL" \
  --command improvements \
  --output "$OUTPUT_DIR/improvements_${TIMESTAMP}.json" || echo "⚠️ Error identificando mejoras"

# 3. Análisis de Satisfacción
echo -e "${GREEN}3. Analizando satisfacción del cliente...${NC}"
python3 "$SCRIPT_DIR/troubleshooting_analyzer.py" \
  --db-url "$DB_URL" \
  --command satisfaction \
  --days "$DAYS" \
  --output "$OUTPUT_DIR/satisfaction_${TIMESTAMP}.json" || echo "⚠️ Error en análisis de satisfacción"

# 4. Reporte Ejecutivo
echo -e "${GREEN}4. Generando reporte ejecutivo...${NC}"
python3 "$SCRIPT_DIR/troubleshooting_analyzer.py" \
  --db-url "$DB_URL" \
  --command executive \
  --days "$DAYS" \
  --output "$OUTPUT_DIR/executive_${TIMESTAMP}.json" || echo "⚠️ Error generando reporte ejecutivo"

# 5. Resumen Rápido
echo -e "${GREEN}5. Obteniendo resumen ejecutivo...${NC}"
python3 "$SCRIPT_DIR/troubleshooting_analyzer.py" \
  --db-url "$DB_URL" \
  --command summary \
  --output "$OUTPUT_DIR/summary_${TIMESTAMP}.json" || echo "⚠️ Error obteniendo resumen"

# 6. Optimización (opcional)
if [ "${OPTIMIZE:-false}" = "true" ]; then
  echo -e "${GREEN}6. Optimizando tablas...${NC}"
  python3 "$SCRIPT_DIR/troubleshooting_analyzer.py" \
    --db-url "$DB_URL" \
    --command optimize \
    --output "$OUTPUT_DIR/optimization_${TIMESTAMP}.json" || echo "⚠️ Error en optimización"
fi

echo ""
echo -e "${BLUE}✅ Análisis completado${NC}"
echo "Reportes guardados en: $OUTPUT_DIR"
echo ""
echo "Archivos generados:"
ls -lh "$OUTPUT_DIR"/*"${TIMESTAMP}"* 2>/dev/null || echo "No se generaron archivos"

# Enviar notificación si está configurado
if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
  echo -e "${YELLOW}Enviando notificación a Slack...${NC}"
  curl -X POST "$SLACK_WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    -d "{\"text\": \"✅ Análisis de troubleshooting completado. Reportes en: $OUTPUT_DIR\"}" \
    || echo "⚠️ Error enviando notificación"
fi



