#!/usr/bin/env bash
# Optimiza el workflow: sugiere mejoras en el orden de ejecución de scripts

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "⚙️  Análisis de Workflow"
echo "======================"
echo ""

# Analizar dependencias entre scripts
echo "📋 Dependencias detectadas:"
echo ""

cat <<EOF
1. Setup inicial
   └─ bash tools/install_dependencies.sh
   └─ (Crear tokens.json desde tokens.example.json)

2. Validación inicial
   └─ bash tools/quick_audit.sh          # Rápido (30s)
   └─ bash tools/ci_validate.sh         # Estructura básica

3. Aplicar configuración
   └─ node tools/apply_tokens.js        # Aplicar tokens
   └─ node tools/sync_tokens_all_platforms.js  # Sincronizar
   └─ bash tools/sync_assets_across_platforms.sh  # Cross-platform

4. Generar assets
   └─ node tools/generate_qr.js         # QR codes
   └─ node tools/generate_variants.js   # Variantes

5. Optimización
   └─ bash tools/optimize_svg.sh        # Optimizar SVGs
   └─ bash tools/export_png.sh          # Exportar PNGs

6. Validación final
   └─ bash tools/health_check.sh        # Health check completo
   └─ bash tools/run_all_validations.sh  # Todas las validaciones

7. Reportes y análisis
   └─ bash tools/analyze_assets.sh      # Análisis completo
   └─ node tools/smart_recommendations.js # Recomendaciones
   └─ bash tools/generate_full_report.sh # Reporte consolidado

8. Empaquetado
   └─ bash tools/package_assets.sh       # Crear ZIP

EOF

echo ""
echo "💡 Workflow optimizado sugerido:"
echo ""

cat > "$ROOT_DIR/exports/optimized_workflow.sh" <<'WORKFLOW_EOF'
#!/usr/bin/env bash
# Workflow optimizado - ejecuta todo en el orden correcto

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 Workflow Optimizado"
echo "====================="
echo ""

# 1. Setup
echo "1️⃣  Setup inicial..."
bash tools/install_dependencies.sh

# 2. Validación rápida
echo ""
echo "2️⃣  Validación rápida..."
bash tools/quick_audit.sh

# 3. Aplicar tokens
echo ""
echo "3️⃣  Aplicando configuración..."
node tools/apply_tokens.js
bash tools/sync_assets_across_platforms.sh

# 4. Generar assets
echo ""
echo "4️⃣  Generando assets..."
node tools/generate_qr.js
node tools/generate_variants.js --type discount || true

# 5. Optimizar
echo ""
echo "5️⃣  Optimizando..."
bash tools/optimize_svg.sh
bash tools/export_png.sh

# 6. Validación
echo ""
echo "6️⃣  Validación final..."
bash tools/health_check.sh
bash tools/run_all_validations.sh || true

# 7. Reportes
echo ""
echo "7️⃣  Generando reportes..."
node tools/smart_recommendations.js
bash tools/generate_full_report.sh

# 8. Empaquetado
echo ""
echo "8️⃣  Empaquetando..."
bash tools/package_assets.sh

echo ""
echo "✅ Workflow completado!"
echo "📊 Ver reportes en: exports/reports/"
echo "📦 ZIPs en: exports/"

WORKFLOW_EOF

chmod +x "$ROOT_DIR/exports/optimized_workflow.sh"

echo "✅ Workflow optimizado generado: exports/optimized_workflow.sh"
echo ""
echo "Para ejecutar el workflow completo:"
echo "   bash exports/optimized_workflow.sh"
echo ""
echo "Tiempo estimado: 5-10 minutos"

