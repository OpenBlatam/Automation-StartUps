#!/usr/bin/env bash
# Auditoría de seguridad: verifica tokens, secrets y configuraciones sensibles

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AUDIT_REPORT="$ROOT_DIR/exports/security_audit_$(date +%Y%m%d_%H%M%S).txt"

echo "🔒 Auditoría de Seguridad"
echo "========================"
echo ""

ISSUES=0
WARNINGS=0

# 1. Verificar tokens con valores sensibles en código
echo "1️⃣  Verificando exposición de tokens..."
if grep -r "password\|secret\|api_key\|private_key" "$ROOT_DIR/design" "$ROOT_DIR/ads" 2>/dev/null | grep -v "example\|placeholder" | head -5 | grep -q .; then
  echo "   ⚠️  Posibles secretos encontrados en assets"
  ((WARNINGS++))
else
  echo "   ✅ No se encontraron secretos expuestos"
fi

# 2. Verificar tokens.json en .gitignore
echo ""
echo "2️⃣  Verificando .gitignore..."
if [ -f "$ROOT_DIR/.gitignore" ]; then
  if grep -q "tokens.json" "$ROOT_DIR/.gitignore"; then
    echo "   ✅ tokens.json está en .gitignore"
  else
    echo "   ⚠️  tokens.json NO está en .gitignore"
    ((WARNINGS++))
  fi
else
  echo "   ⚠️  .gitignore no encontrado"
  ((WARNINGS++))
fi

# 3. Verificar permisos de archivos sensibles
echo ""
echo "3️⃣  Verificando permisos..."
if [ -f "$ROOT_DIR/design/instagram/tokens.json" ]; then
  PERMS=$(stat -f "%OLp" "$ROOT_DIR/design/instagram/tokens.json" 2>/dev/null || stat -c "%a" "$ROOT_DIR/design/instagram/tokens.json" 2>/dev/null || echo "000")
  if [ "$PERMS" != "600" ] && [ "$PERMS" != "644" ]; then
    echo "   ⚠️  Permisos de tokens.json: $PERMS (recomendado: 600 o 644)"
    ((WARNINGS++))
  else
    echo "   ✅ Permisos de tokens.json correctos: $PERMS"
  fi
fi

# 4. Verificar que no haya URLs hardcodeadas inseguras
echo ""
echo "4️⃣  Verificando URLs inseguras..."
if grep -r "http://" "$ROOT_DIR/design" "$ROOT_DIR/ads" --include="*.svg" 2>/dev/null | grep -v "example\|placeholder" | head -3 | grep -q .; then
  echo "   ⚠️  URLs HTTP encontradas (usar HTTPS)"
  ((WARNINGS++))
else
  echo "   ✅ No se encontraron URLs HTTP"
fi

# 5. Verificar backups con información sensible
echo ""
echo "5️⃣  Verificando backups..."
BACKUP_DIR="$ROOT_DIR/backups/assets"
if [ -d "$BACKUP_DIR" ]; then
  BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*.tar.gz" 2>/dev/null | wc -l | xargs)
  if [ "$BACKUP_COUNT" -gt 0 ]; then
    # Verificar que backups no estén en repositorio público
    if [ -f "$ROOT_DIR/.gitignore" ]; then
      if grep -q "backups/" "$ROOT_DIR/.gitignore"; then
        echo "   ✅ Backups están en .gitignore"
      else
        echo "   ⚠️  Backups NO están en .gitignore"
        ((WARNINGS++))
      fi
    fi
    echo "   ℹ️  Total de backups: $BACKUP_COUNT"
  else
    echo "   ℹ️  No hay backups aún"
  fi
else
  echo "   ℹ️  Directorio de backups no existe"
fi

# 6. Verificar configuraciones de CI/CD
echo ""
echo "6️⃣  Verificando CI/CD..."
if [ -d "$ROOT_DIR/.github" ]; then
  if grep -r "secret\|password\|api_key" "$ROOT_DIR/.github" 2>/dev/null | grep -v "example\|placeholder" | head -3 | grep -q .; then
    echo "   ⚠️  Posibles secretos en configuraciones CI/CD"
    ((WARNINGS++))
  else
    echo "   ✅ Configuraciones CI/CD limpias"
  fi
fi

# 7. Verificar archivos de configuración expuestos
echo ""
echo "7️⃣  Verificando archivos de configuración..."
CONFIG_FILES=(
  "design/instagram/tokens.json"
  "ads/linkedin/tokens.json"
)

for config_file in "${CONFIG_FILES[@]}"; do
  if [ -f "$ROOT_DIR/$config_file" ]; then
    # Verificar que no esté versionado (si es git repo)
    if [ -d "$ROOT_DIR/.git" ]; then
      if git check-ignore -q "$ROOT_DIR/$config_file" 2>/dev/null; then
        echo "   ✅ $config_file está en .gitignore"
      else
        echo "   ⚠️  $config_file NO está en .gitignore (puede estar versionado)"
        ((WARNINGS++))
      fi
    fi
  fi
fi

# Generar reporte
mkdir -p "$(dirname "$AUDIT_REPORT")"
{
  echo "Reporte de Auditoría de Seguridad"
  echo "================================="
  echo "Fecha: $(date)"
  echo ""
  echo "Resumen:"
  echo "  Advertencias: $WARNINGS"
  echo ""
  echo "Recomendaciones:"
  echo "  1. Asegurar que tokens.json esté en .gitignore"
  echo "  2. Verificar permisos de archivos sensibles (600 recomendado)"
  echo "  3. Usar HTTPS en todas las URLs"
  echo "  4. No hardcodear secretos en código"
  echo "  5. Revisar configuraciones CI/CD regularmente"
  echo ""
  echo "✅ Auditoría completada"
} > "$AUDIT_REPORT"

# Resumen
echo ""
echo "========================"
echo "📊 Resumen:"
echo "  ⚠️  Advertencias: $WARNINGS"
echo ""
echo "📄 Reporte guardado: $AUDIT_REPORT"
echo ""

if [ $WARNINGS -gt 0 ]; then
  echo "💡 Revisa las advertencias arriba"
  exit 1
else
  echo "✅ Auditoría de seguridad: PASÓ"
  exit 0
fi

