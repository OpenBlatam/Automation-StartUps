# 🚀 Quick Start - Campaña Instagram 35% OFF

Guía rápida para poner en marcha el sistema completo en 5 minutos.

## Paso 1: Instalar dependencias

```bash
bash tools/install_dependencies.sh
```

Esto instalará:
- `qrcode` (Node.js) para generar QR
- `svgo` (global) para optimizar SVG
- Verificará Inkscape/rsvg-convert para exportar PNG

## Paso 2: Configurar tokens

1. Copia el template:
   ```bash
   cp design/instagram/tokens.example.json design/instagram/tokens.json
   ```

2. Edita `design/instagram/tokens.json` con tus datos:
   - URL de tu sitio
   - Handle de Instagram
   - Código de cupón
   - CTA personalizado
   - Colores de marca (opcional)

## Paso 3: Aplicar UTM (opcional)

Si quieres trackear por mercado:
```bash
node tools/apply_market_utm.js es  # o en/pt
```

Edita `design/instagram/utm_presets.json` para personalizar campañas.

## Paso 4: Sincronizar con LinkedIn (opcional)

Si tienes assets de LinkedIn:
```bash
node tools/sync_tokens_all_platforms.js
```

Esto sincronizará tokens desde Instagram a LinkedIn.

## Paso 5: Health Check (recomendado)

Antes de hacer build, verifica que todo esté bien:
```bash
bash tools/health_check.sh
```

Esto verificará:
- Estructura de directorios
- Tokens configurados
- SVGs vacíos/rotos
- Rutas del preview
- Dependencias instaladas

## Paso 6: Validar y build

```bash
# Validar que todo esté en orden
bash tools/validate_all.sh

# Build completo Instagram + LinkedIn:
bash tools/build_all_platforms.sh

# O solo Instagram:
bash tools/build_all.sh
```

## Paso 6: Revisar

1. **Preview web**: Abre `exports/preview/index.html` en tu navegador
2. **PNG exportados**: Revisa `exports/png/1x/` y `exports/png/2x/`
3. **ZIP final**: `exports/package_instagram_*.zip`

## Próximos pasos

- Reemplaza los placeholders de logo en los SVG
- Revisa los copys en `design/instagram/copys/`
- Consulta el calendario en `design/instagram/calendar/post_calendar.csv`
- Completa el QA checklist: `design/instagram/qa/qa_checklist.md`
- Usa el checklist de entrega: `DELIVERY_CHECKLIST.md`

## Comandos Rápidos

### Auditoría Rápida (30 segundos)
```bash
bash tools/quick_audit.sh          # Verificación esencial
```

### Auto-fix de Problemas
```bash
bash tools/auto_fix_issues.sh      # Corregir automáticamente problemas comunes
```

### Watch Mode (Desarrollo)
```bash
bash tools/watch_assets.sh         # Monitorea cambios y valida automáticamente
```

### Recomendaciones Inteligentes
```bash
node tools/smart_recommendations.js # Análisis y sugerencias basadas en mejores prácticas
```

### Sincronización Multi-Plataforma
```bash
bash tools/sync_assets_across_platforms.sh  # Sincroniza tokens entre Instagram, LinkedIn, Webinars
```

### Operaciones en Lote
```bash
bash tools/batch_operations.sh --all --platform INSTAGRAM  # Ejecutar múltiples operaciones
```

### Benchmark de Performance
```bash
bash tools/benchmark_performance.sh  # Medir tiempos de ejecución de scripts
```

### Health Score
```bash
node tools/health_score_calculator.js  # Calcular health score del sistema (0-100)
```

### Backup Automático
```bash
bash tools/auto_backup.sh  # Crear backup con rotación automática
```

### Comparar Versiones
```bash
bash tools/compare_versions.sh --backup1 backups/assets_backup_20240101.tar.gz --backup2 backups/assets_backup_20240102.tar.gz
```

### Exportar para Figma
```bash
node tools/export_to_figma_ready.js  # Genera CSV y guía para importar a Figma
```

## Scripts útiles

```bash
# Validación y health check
bash tools/run_all_validations.sh         # Ejecutar todas las validaciones
bash tools/health_check.sh                # Health check completo
bash tools/validate_svg_integrity.sh      # Validar integridad SVG
bash tools/check_dimensions.sh            # Verificar dimensiones SVG
node tools/check_token_coverage.js        # Verificar tokens aplicados
bash tools/fix_broken_svgs.sh             # Reparar SVGs rotos
node tools/validate_preview_paths.js      # Validar rutas del preview

# Análisis y reportes
bash tools/analyze_assets.sh              # Análisis completo de assets
node tools/generate_assets_metrics.js      # Métricas avanzadas (JSON)
bash tools/benchmark_assets.sh            # Benchmark de tamaño/rendimiento
bash tools/find_duplicates.sh              # Encontrar duplicados
bash tools/optimize_assets_report.sh       # Reporte de optimización
bash tools/generate_executive_summary.sh  # Resumen ejecutivo

# Tokens y temas
node tools/apply_tokens.js                # Aplicar tokens Instagram
node tools/sync_tokens_all_platforms.js   # Sincronizar tokens
node tools/apply_tokens_linkedin.js       # Aplicar tokens LinkedIn
node tools/apply_theme.js                 # Aplicar tema/colores

# Generación y exportación
node tools/generate_qr.js                 # Generar QR
bash tools/export_png.sh                  # Exportar PNG (1x/2x)
node tools/generate_variants.js           # Generar variantes (--perc=25,40,50 --urg="...")
bash tools/optimize_svg.sh                # Optimizar SVG con SVGO

# Reportes y visualización
bash tools/generate_full_report.sh        # Reporte completo consolidado
bash tools/generate_assets_summary.sh     # Resumen ejecutivo visual
bash tools/track_changes.sh               # Trackear cambios (primera vez crea línea base)
open exports/assets_summary.html          # Resumen ejecutivo
open exports/advanced_assets_dashboard.html  # Dashboard avanzado
open exports/preview/index.html           # Preview de assets
open tools/create_assets_dashboard.html   # Dashboard simple
```

## Troubleshooting

**Error: "qrcode not found"**
- Ejecuta: `npm install qrcode`

**Error: "svgo not found"**
- Ejecuta: `npm install -g svgo`

**Error: "inkscape not found"**
- macOS: `brew install --cask inkscape`
- Linux: `sudo apt-get install inkscape`
- O usa `rsvg-convert` como alternativa

**SVG no se ve en preview**
- Verifica que las rutas sean correctas
- Algunos navegadores requieren servidor local para SVG (usa `python3 -m http.server`)

---

¿Listo para comenzar? Ejecuta el Paso 1 y sigue en orden. 🎨
