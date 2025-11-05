#!/usr/bin/env bash
# Genera un plan de migración para actualizar assets de una versión a otra

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLAN_FILE="$ROOT_DIR/exports/migration_plan.md"

echo "📋 Generando plan de migración..."
echo ""

cat > "$PLAN_FILE" <<EOF
# Plan de Migración de Assets

Generado: $(date '+%Y-%m-%d %H:%M:%S')

## Pre-migración

### 1. Backup
\`\`\`bash
# Crear backup completo
tar -czf backup_\$(date +%Y%m%d).tar.gz design/ exports/ ads/
\`\`\`

### 2. Validación Previa
\`\`\`bash
# Ejecutar validaciones
bash tools/health_check.sh
bash tools/validate_svg_integrity.sh
bash tools/run_all_validations.sh
\`\`\`

### 3. Reporte de Estado Actual
\`\`\`bash
# Generar reporte completo
bash tools/generate_full_report.sh
\`\`\`

## Proceso de Migración

### Paso 1: Actualizar Tokens
\`\`\`bash
# Editar tokens.json con nuevos valores
# Luego aplicar:
node tools/apply_tokens.js
node tools/sync_tokens_all_platforms.js
\`\`\`

### Paso 2: Regenerar Assets Críticos
\`\`\`bash
# Build completo
bash tools/build_all_platforms.sh
\`\`\`

### Paso 3: Validar Post-Migración
\`\`\`bash
# Verificar que todo esté correcto
bash tools/ci_validate.sh
bash tools/run_all_validations.sh
\`\`\`

### Paso 4: Generar Nuevos Reportes
\`\`\`bash
# Comparar con versión anterior
bash tools/track_changes.sh
bash tools/generate_full_report.sh
\`\`\`

## Checklist Post-Migración

- [ ] Todos los tokens aplicados
- [ ] SVGs válidos (sin vacíos, sin errores)
- [ ] Dimensiones correctas
- [ ] QR codes generados
- [ ] PNG exportados (1x y 2x)
- [ ] Preview actualizado
- [ ] Reportes generados
- [ ] Health check: OK
- [ ] CI/CD validation: PASÓ

## Rollback (si es necesario)

\`\`\`bash
# Restaurar backup
tar -xzf backup_YYYYMMDD.tar.gz
\`\`\`

## Notas

- Revisar cambios con: \`bash tools/track_changes.sh\`
- Ver reportes completos en: \`exports/reports/\`
- Dashboard: \`exports/assets_summary.html\`

EOF

echo "✅ Plan de migración generado: $PLAN_FILE"
echo "📄 Revisa y personaliza según tus necesidades"


