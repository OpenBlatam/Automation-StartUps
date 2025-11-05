# 📚 Índice Maestro de Herramientas

Total de herramientas: **45+ scripts**

Última actualización: $(date '+%Y-%m-%d %H:%M:%S')

## 🚀 Inicio Rápido

### Setup y Configuración
- `install_dependencies.sh` - Instalar todas las dependencias
- `quick_audit.sh` - Auditoría rápida (30 segundos)
- `ci_validate.sh` - Validación para CI/CD

### Workflow Principal
- `build_all.sh` - Build completo Instagram
- `build_all_platforms.sh` - Build multi-plataforma
- `optimized_workflow.sh` (generado) - Workflow optimizado completo

## 🔧 Automatización y Tokens

### Gestión de Tokens
- `apply_tokens.js` - Aplicar tokens a SVGs
- `sync_tokens_all_platforms.js` - Sincronizar tokens entre plataformas
- `sync_assets_across_platforms.sh` - Sincronización completa cross-platform
- `check_token_coverage.js` - Verificar cobertura de tokens

### Tema y Branding
- `apply_theme.js` - Aplicar colores de marca
- `apply_market_utm.js` - Aplicar UTM por mercado

## 🎨 Generación de Assets

### QR Codes y Variantes
- `generate_qr.js` - Generar códigos QR
- `generate_variants.js` - Crear variantes (descuento, urgencia, A/B)

### Exportación y Optimización
- `export_png.sh` - Exportar PNG 1x y 2x
- `optimize_svg.sh` - Optimizar SVGs con SVGO
- `package_assets.sh` - Crear ZIP de entrega

## ✅ Validación y QA

### Validaciones Individuales
- `validate_svg_integrity.sh` - Integridad de SVGs
- `check_dimensions.sh` - Verificar dimensiones
- `validate_preview_paths.js` - Validar rutas del preview
- `fix_broken_svgs.sh` - Reparar SVGs rotos

### Validaciones Completas
- `run_all_validations.sh` - Ejecutar todas las validaciones
- `health_check.sh` - Health check completo
- `validate_all.sh` - Validación básica

### Auto-Fix y Mantenimiento
- `auto_fix_issues.sh` - Auto-corregir problemas comunes
- `watch_assets.sh` - Watch mode (monitoreo en tiempo real)

## 📊 Análisis y Reportes

### Análisis de Assets
- `analyze_assets.sh` - Análisis completo con métricas
- `smart_recommendations.js` - Recomendaciones inteligentes
- `benchmark_performance.sh` - Benchmark de rendimiento

### Reportes Consolidados
- `generate_full_report.sh` - Reporte completo consolidado
- `generate_assets_summary.sh` - Resumen ejecutivo visual
- `generate_executive_summary.sh` - Resumen ejecutivo detallado
- `track_changes.sh` - Tracking de cambios temporales

### Utilidades de Reportes
- `cleanup_reports.sh` - Limpiar reportes antiguos
- `generate_changelog.sh` - Generar changelog

## 🔄 Operaciones Avanzadas

### Workflow y Optimización
- `optimize_workflow.sh` - Analizar y optimizar workflow
- `batch_operations.sh` - Operaciones en lote

### Integración Multi-Plataforma
- `integrate_webinars.sh` - Integrar webinars al sistema
- `apply_tokens_linkedin.js` - Aplicar tokens a LinkedIn

### UTM y URLs
- `build_utm_url.js` - Builder de URLs con UTM

## 📱 Dashboards y Visualización

### Previews y Dashboards
- `index.html` (exports/preview/) - Preview principal con filtros
- `create_assets_dashboard.html` - Dashboard de assets
- `create_realtime_dashboard.html` - Dashboard en tiempo real
- `advanced_assets_dashboard.html` - Dashboard avanzado
- `assets_summary.html` - Resumen ejecutivo visual

## 🎯 Casos de Uso Comunes

### Primera vez / Setup
```bash
bash tools/install_dependencies.sh
bash tools/quick_audit.sh
bash tools/auto_fix_issues.sh
```

### Desarrollo / Iteración
```bash
bash tools/watch_assets.sh  # En una terminal
# Editar assets...
# Validación automática en tiempo real
```

### Pre-Build
```bash
bash tools/quick_audit.sh
bash tools/auto_fix_issues.sh
node tools/smart_recommendations.js
```

### Build Completo
```bash
bash tools/build_all_platforms.sh
# O workflow optimizado:
bash exports/optimized_workflow.sh
```

### Validación Completa
```bash
bash tools/run_all_validations.sh
bash tools/health_check.sh
bash tools/ci_validate.sh
```

### Generar Reportes
```bash
bash tools/generate_full_report.sh
bash tools/generate_assets_summary.sh
node tools/smart_recommendations.js
```

### Operaciones en Lote
```bash
# Aplicar tokens y exportar PNGs
bash tools/batch_operations.sh --apply-tokens --export-png

# Optimizar y validar
bash tools/batch_operations.sh --optimize --validate

# Todo en Instagram
bash tools/batch_operations.sh --all --platform INSTAGRAM
```

### CI/CD
```bash
bash tools/ci_validate.sh  # Falla si hay errores críticos
bash tools/benchmark_performance.sh  # Tracking de performance
```

## 📈 Métricas y Monitoreo

- Health Score (0-100)
- Asset Count (SVGs, PNGs)
- Token Coverage
- Validation Status
- Performance Benchmarks
- Recommendations Score

## 🔗 Archivos de Configuración

- `tokens.json` - Configuración principal
- `tokens.example.json` - Template
- `utm_presets.json` - Presets UTM por mercado

## 📦 Estructura de Outputs

```
exports/
├── png/              # PNGs exportados (1x, 2x)
├── svg_opt/          # SVGs optimizados
├── preview/           # Previews HTML
├── reports/           # Reportes consolidados
├── benchmark_*.json   # Benchmarks de performance
├── smart_recommendations.json  # Recomendaciones
└── package_*.zip      # ZIPs finales
```

## 💡 Tips y Mejores Prácticas

1. **Siempre ejecuta `quick_audit.sh`** antes de empezar
2. **Usa `auto_fix_issues.sh`** para correcciones automáticas
3. **`smart_recommendations.js`** ofrece insights valiosos
4. **`watch_assets.sh`** durante desarrollo para feedback inmediato
5. **`batch_operations.sh`** para operaciones repetitivas
6. **`sync_assets_across_platforms.sh`** para mantener consistencia

## 🆘 Solución de Problemas

### Problemas comunes → Solución rápida
- SVGs vacíos → `bash tools/fix_broken_svgs.sh`
- Tokens no aplicados → `bash tools/auto_fix_issues.sh`
- Health score bajo → `node tools/smart_recommendations.js`
- Validación falla → `bash tools/run_all_validations.sh`
- Performance lento → `bash tools/benchmark_performance.sh`

## 📚 Documentación Adicional

- `readme.md` - Documentación principal
- `QUICKSTART.md` - Guía rápida
- `docs/VALIDATION_GUIDE.md` - Guía de validación (si existe)
- `DELIVERY_CHECKLIST.md` - Checklist de entrega

