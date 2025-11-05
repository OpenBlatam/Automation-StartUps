# Paquete Completo Instagram 35% OFF

Sistema completo de diseño y automatización para campaña de descuento del 35% por 48 horas.

## 📦 Contenido

### Artes principales
- **Feed 1080×1080**: 3 anuncios base + variantes (dark, A/B, últimas 24h, low-text)
- **Stories 1080×1920**: 3 stories + variantes dark
- **Reels**: 3 portadas 1080×1920
- **Carrusel**: 3 slides (hook, beneficios, CTA)
- **Highlights**: 4 portadas temáticas
- **Ads Instagram**: 1080×1350 (feed vertical 4:5) para los 3 anuncios
- **LinkedIn**: Assets 1200×627 existentes (integrados al sistema de tokens)
- **Webinars**: Prerolls y thumbnails (integrables al sistema)

### Automatización
- **Tokens**: Reemplazo masivo de URL/handle/cupón/CTA
- **Tema**: Aplicación de colores de marca en todos los SVG
- **UTM**: Generación y aplicación de parámetros por mercado (ES/EN/PT)
- **QR**: Generación automática desde URL con UTM
- **Variantes**: Script para crear variantes de descuento/urgencia
- **Export**: PNG 1x/2x automático
- **Optimización**: SVGO para reducir tamaños

### Recursos
- **Copys**: ES/EN/PT con hooks, CTAs y hashtags
- **Calendario**: CSV con slots sugeridos de publicación
- **Accesibilidad**: Alt text para todos los artes (ES/EN/PT)
- **QA**: Checklist previo a publicación

## 🚀 Inicio rápido

**Guía completa**: Ver `QUICKSTART.md` para paso a paso detallado.

### Método Rápido (CLI Unificado)
```bash
bash tools/cli.sh setup      # Configuración inicial
bash tools/cli.sh validate    # Validación completa
bash tools/cli.sh build      # Build completo
bash tools/cli.sh status     # Estado del sistema
```

### Método Manual

1. **Instala dependencias**:
   ```bash
   bash tools/install_dependencies.sh
   ```

2. **Configura tokens**: Copia `design/instagram/tokens.example.json` a `tokens.json` y edita con tus datos

3. **Valida y build**:
   ```bash
   bash tools/validate_all.sh
   # Build Instagram + LinkedIn:
   bash tools/build_all_platforms.sh
   # O solo Instagram:
   bash tools/build_all.sh
   ```

4. **Preview**: Abre `exports/preview/index.html`

## 📁 Estructura

```
design/instagram/
├── 1080x1080/          # Feed principal
├── 1080x1350/          # Ads feed vertical
├── 1080x1920/          # Stories
├── reels/              # Portadas Reels
├── highlights/         # Portadas Highlights
├── carousel/           # Slides carrusel
├── copys/              # Captions ES/EN/PT
├── calendar/           # Calendario CSV
├── accessibility/      # Alt text
├── qa/                 # Checklist QA
├── tokens.json         # Configuración
└── utm_presets.json    # UTMs por mercado

tools/
├── apply_tokens.js     # Reemplazo masivo
├── apply_theme.js      # Aplicar colores marca
├── apply_market_utm.js # UTM por mercado
├── build_utm_url.js   # Builder UTM custom
├── generate_qr.js      # Generar QR
├── generate_variants.js # Variantes descuento/urgencia
├── export_png.sh       # Export PNG 1x/2x
├── optimize_svg.sh     # Optimizar con SVGO
├── package_assets.sh   # Crear ZIP
└── build_all.sh        # Script maestro

exports/
├── png/1x/             # PNG 1080
├── png/2x/             # PNG 2160
├── svg_opt/            # SVG optimizados
├── preview/            # Preview web HTML
└── package_*.zip       # ZIP final
```

## 🔧 Scripts individuales

- `bash tools/validate_all.sh` - Validar que todos los archivos críticos estén presentes
- `bash tools/build_all.sh` - Script maestro Instagram (ejecuta todo el flujo)
- `bash tools/build_all_platforms.sh` - Build completo Instagram + LinkedIn
- `bash tools/integrate_webinars.sh` - Integrar webinars al sistema (organiza prerolls/square/vertical)
- `bash tools/generate_executive_summary.sh` - Generar resumen ejecutivo completo
- `bash tools/analyze_assets.sh` - Generar reporte de análisis de assets (incluye LinkedIn y webinars)
- `bash tools/run_all_validations.sh` - **Ejecutar todas las validaciones en secuencia** (recomendado)
- `bash tools/generate_full_report.sh` - **Generar reporte completo consolidado** (todos los análisis en uno)
- `bash tools/generate_assets_summary.sh` - Generar resumen ejecutivo visual HTML
- `bash tools/track_changes.sh` - Trackear cambios en assets (comparación temporal)
- `bash tools/cleanup_reports.sh [N]` - Limpiar reportes antiguos (mantiene últimos N, default: 10)
- `bash tools/health_check.sh` - Health check completo del sistema (estructura, tokens, SVGs, preview)
- `bash tools/validate_svg_integrity.sh` - Validar integridad de todos los SVG (vacíos, estructura, dimensiones)
- `bash tools/check_dimensions.sh` - Verificar que todos los SVG tengan dimensiones correctas
- `node tools/check_token_coverage.js` - Verificar cobertura de tokens aplicados
- `bash tools/fix_broken_svgs.sh` - Reparar o eliminar SVGs vacíos/rotos
- `node tools/validate_preview_paths.js` - Validar que todas las rutas del preview existan
- `bash tools/auto_fix_issues.sh` - **Auto-corregir problemas comunes automáticamente**
- `bash tools/ci_validate.sh` - **Validación para CI/CD** (falla si hay errores críticos)
- `bash tools/quick_audit.sh` - **Auditoría rápida** (30 segundos, verificación esencial)
- `bash tools/watch_assets.sh` - **Watch mode**: monitorea cambios y valida automáticamente
- `node tools/smart_recommendations.js` - **Recomendaciones inteligentes** basadas en análisis
- `bash tools/benchmark_performance.sh` - **Benchmark de rendimiento** (mide tiempos de ejecución)
- `bash tools/sync_assets_across_platforms.sh` - **Sincronizar assets entre plataformas** (Instagram, LinkedIn, Webinars)
- `bash tools/optimize_workflow.sh` - **Analizar y optimizar workflow** (sugiere mejoras)
- `bash tools/batch_operations.sh` - **Operaciones en lote** (ejecutar múltiples operaciones)
- `bash tools/auto_backup.sh` - **Backup automático con rotación** (mantiene últimos N backups)
- `bash tools/compare_versions.sh` - **Comparar versiones** de assets (detecta cambios)
- `node tools/generate_comparison_report.js` - **Reporte comparativo visual** de métricas
- `node tools/export_to_figma_ready.js` - **Preparar assets para Figma** (CSV + guía)
- `node tools/health_score_calculator.js` - **Calculadora de health score** (0-100)
- `bash tools/scheduled_tasks.sh` - **Sistema de tareas programadas** (daily, weekly, monthly)
- `bash tools/performance_optimizer.sh` - **Optimizador de rendimiento** (analiza y sugiere mejoras)
- `bash tools/collaboration_helper.sh` - **Herramientas de colaboración** (onboarding, tareas, notas)
- `node tools/generate_api_docs.js` - **Generar documentación de API** (auto-generada)
- `node tools/smart_alerts.js` - **Sistema de alertas inteligentes** (basado en umbrales)
- `bash tools/export_multiformat.sh` - **Exportación multi-formato** (PNG, JPG, WebP)
- `node tools/test_assets.js` - **Suite de tests** (validación automatizada)
- `bash tools/maintenance_mode.sh` - **Modo mantenimiento** (limpieza + optimización)
- `node tools/metrics_tracker.js` - **Sistema de tracking de métricas** (historial temporal)
- `bash tools/security_audit.sh` - **Auditoría de seguridad** (tokens, permisos, .gitignore)
- `node tools/generate_compliance_report.js` - **Reporte de compliance** (cumplimiento de estándares)
- `bash tools/continuous_monitor.sh` - **Monitoreo continuo** (daemon mode con verificaciones periódicas)
- `bash tools/cli.sh` - **CLI Unificado** - Interfaz de línea de comandos para todas las herramientas
- `bash tools/integration_webhook.sh` - **Integración webhook** (notificaciones a servicios externos)
- `bash tools/optimize_all.sh` - **Optimización completa** (todas las optimizaciones en uno)
- `node tools/predictive_analysis.js` - **Análisis predictivo** (predice tendencias y problemas)
- `bash tools/notify_system.sh` - **Sistema de notificaciones** (multi-canal: Slack, Discord, Email)
- `bash tools/quick_start_guide.sh` - **Guía interactiva de inicio** (setup paso a paso)
- `bash tools/generate_changelog.sh [version]` - Generar changelog (ej: 1.0.0)
- `node tools/apply_tokens.js` - Aplicar tokens a todos los SVG de Instagram
- `node tools/sync_tokens_all_platforms.js` - Sincronizar tokens a LinkedIn y otras plataformas
- `node tools/apply_tokens_linkedin.js` - Aplicar tokens a SVG de LinkedIn
- `node tools/apply_theme.js` - Aplicar colores de marca
- `node tools/generate_qr.js` - Generar QR (requiere: `npm install qrcode`)
- `bash tools/export_png.sh` - Exportar PNG (requiere: inkscape o rsvg-convert)
- `bash tools/optimize_svg.sh` - Optimizar SVG (requiere: `npm i -g svgo`)
- `bash tools/package_assets.sh` - Crear ZIP final
- `node tools/generate_variants.js --perc=25,40 --urg="Solo 48 horas,Últimas 24 horas"` - Generar variantes

## 📖 Documentación

- **Quick Start**: `QUICKSTART.md` - Guía rápida de inicio
- **Guía completa**: `design/instagram/1080x1080/README.md`
- **QA Checklist**: `design/instagram/qa/qa_checklist.md`
- **Checklist de entrega**: `DELIVERY_CHECKLIST.md`
- **Changelog**: `CHANGELOG.md` (generar con `bash tools/generate_changelog.sh`)
- **Template tokens**: `design/instagram/tokens.example.json`
- **Alt text**: `design/instagram/accessibility/alt_text.csv`
- **Calendario**: `design/instagram/calendar/post_calendar.csv`
- **Copys**: `design/instagram/copys/copys_instagram_promos.md`
- **Preview web**: `exports/preview/index.html` (con categorías, filtros y stats - incluye LinkedIn)
- **Reporte assets**: `exports/assets_report.txt` (generar con `bash tools/analyze_assets.sh`)
- **Reporte integridad SVG**: `exports/svg_integrity_report.txt` (generar con `bash tools/validate_svg_integrity.sh`)
- **Reporte dimensiones**: `exports/dimensions_report.txt` (generar con `bash tools/check_dimensions.sh`)
- **Métricas avanzadas**: `exports/assets_metrics.json` (generar con `node tools/generate_assets_metrics.js`)
- **Dashboard avanzado**: `exports/advanced_assets_dashboard.html` - Dashboard interactivo con métricas
- **Resumen ejecutivo**: `exports/assets_summary.html` - Vista consolidada de todos los assets y herramientas
- **Reportes consolidados**: `exports/reports/YYYYMMDD_HHMMSS/` - Reportes completos con timestamp
- **Changelog de assets**: `exports/assets_changelog.txt` - Comparación de cambios entre ejecuciones
- **Reporte duplicados**: `exports/duplicates_report.txt` (generar con `bash tools/find_duplicates.sh`)
- **Reporte optimización**: `exports/optimization_opportunities.txt` (generar con `bash tools/optimize_assets_report.sh`)
- **Benchmark**: `exports/benchmark_report.txt` (generar con `bash tools/benchmark_assets.sh`)
- **Guía de validación**: `docs/VALIDATION_GUIDE.md` - Guía completa de todas las herramientas de validación
- **Dashboard assets**: `tools/create_assets_dashboard.html` - Vista resumida de todos los assets
- **Dashboard tiempo real**: `tools/create_realtime_dashboard.html` - Métricas en tiempo real con gráficos
- **Recomendaciones inteligentes**: `exports/smart_recommendations.json` (generar con `node tools/smart_recommendations.js`)
- **Benchmark performance**: `exports/benchmark_*.json` (generar con `bash tools/benchmark_performance.sh`)
- **Workflow optimizado**: `exports/optimized_workflow.sh` (generar con `bash tools/optimize_workflow.sh`)
- **Health score**: `exports/health_score.json` (generar con `node tools/health_score_calculator.js`)
- **Reporte comparativo**: `exports/comparison_report.html` (generar con `node tools/generate_comparison_report.js`)
- **Figma import**: `exports/figma_import.csv` y `exports/FIGMA_IMPORT_GUIDE.md` (generar con `node tools/export_to_figma_ready.js`)
- **Backups**: `backups/assets/` (generar con `bash tools/auto_backup.sh`)
- **Tareas programadas**: `exports/scheduled_tasks.json` (configurar con `bash tools/scheduled_tasks.sh init`)
- **Optimización**: `exports/performance_optimization.txt` (generar con `bash tools/performance_optimizer.sh`)
- **Colaboración**: `.collaboration/` (configurar con `bash tools/collaboration_helper.sh setup`)
- **API Docs**: `docs/API_DOCUMENTATION.md` (generar con `node tools/generate_api_docs.js`)
- **Dashboard maestro**: `tools/create_master_dashboard.html` - Dashboard central con todas las funciones
- **Alertas inteligentes**: `exports/smart_alerts.json` (generar con `node tools/smart_alerts.js`)
- **Test results**: `exports/test_results.json` (generar con `node tools/test_assets.js`)
- **Exportaciones multi-formato**: `exports/png/`, `exports/jpg/`, `exports/webp/` (generar con `bash tools/export_multiformat.sh`)
- **Métricas históricas**: `exports/metrics_history/` y `exports/latest_metrics.json` (generar con `node tools/metrics_tracker.js`)
- **Auditoría seguridad**: `exports/security_audit_*.txt` (generar con `bash tools/security_audit.sh`)
- **Reporte compliance**: `exports/compliance_report.json` y `exports/compliance_report.html` (generar con `node tools/generate_compliance_report.js`)
- **Log de monitoreo**: `exports/monitoring.log` (generar con `bash tools/continuous_monitor.sh`)
- **Resumen ejecutivo**: `EXECUTIVE_SUMMARY.md` (generar con `bash tools/generate_executive_summary.sh`)
- **LinkedIn assets**: `ads/linkedin/` (integrados al sistema de tokens)
  - Template tokens: `ads/linkedin/tokens.example.json`
  - Guía: `ads/linkedin/GUIA_EXPORTACION_ADS.md` (si existe)
- **Webinars**: `webinar-preroll-*.svg` en raíz (integrables con `bash tools/integrate_webinars.sh`)

## 📝 Notas

- Los SVG son editables: abre en Figma/Illustrator para personalizar
- Los placeholders de logo deben reemplazarse por tu marca
- Revisa el QA checklist antes de publicar
- Usa las versiones low-text para Instagram Ads Manager (<20% texto)
- Exporta también PNG @2x (2160) para mayor nitidez

## 🎯 Próximos pasos

1. **Auditoría rápida**: `bash tools/quick_audit.sh` (30 segundos)
2. Configura tus tokens en `design/instagram/tokens.json`
3. **Auto-fix problemas**: `bash tools/auto_fix_issues.sh`
4. Aplica tu tema de marca con `node tools/apply_theme.js`
5. **Recomendaciones**: `node tools/smart_recommendations.js`
6. **Health score**: `node tools/health_score_calculator.js` (ver estado del sistema)
7. Ejecuta `bash tools/build_all.sh` para generar todo
8. **Validación completa**: `bash tools/run_all_validations.sh`
9. **Backup**: `bash tools/auto_backup.sh` (antes de cambios importantes)
10. Revisa el preview en `exports/preview/index.html`
11. **Dashboard tiempo real**: `tools/create_realtime_dashboard.html`
12. Publica según el calendario en `design/instagram/calendar/post_calendar.csv`

## ⚡ Workflow Optimizado

Para un workflow completo automatizado:
```bash
bash exports/optimized_workflow.sh
```

Este script ejecuta todas las operaciones en el orden correcto (setup → validación → build → reportes).
