# 🛠️ Herramientas de Gestión de Creativos

Guía completa de todas las herramientas disponibles en el sistema.

## 📋 Índice de Herramientas

### 🔍 Análisis y Validación
- `analyze_assets.sh` - Análisis completo de assets con estadísticas avanzadas
- `validate_utms.py` - Validación de UTMs y consistencia
- `health_check.sh` - Health check rápido
- `quick_status.py` - Status rápido en una línea

### 📊 Performance y Analytics
- `analyze_real_time_performance.py` - Performance en tiempo real desde APIs
- `predict_creative_performance.py` - Predicción de performance basada en benchmarks
- `analyze_trends.py` - Análisis de tendencias temporales
- `benchmark_creatives.py` - Benchmarking vs. estándares de industria
- `correlation_analysis.py` - Análisis de correlaciones entre variables

### 💰 ROI y Optimización
- `calculate_roi_and_optimize.py` - Cálculo de ROI y optimización de budget
- `auto_optimization_engine.py` - Motor de optimización automática
- `machine_learning_optimizer.py` - Optimización basada en ML

### 🧪 Testing y Experimentación
- `automated_ab_testing.py` - A/B testing automatizado con significancia estadística
- `compare_creative_performance.py` - Comparación de performance

### 📈 Forecasting y Predicción
- `advanced_forecasting.py` - Forecasting avanzado (3 meses)
- `generate_performance_report.py` - Reporte completo de performance

### 🚨 Alertas y Monitoreo
- `check_alerts.py` - Sistema de alertas proactivo
- `detect_anomalies.py` - Detección de anomalías estadísticas
- `continuous_health_monitor.py` - Monitor continuo de salud

### 💡 Recomendaciones
- `intelligent_recommendations.py` - Recomendaciones inteligentes contextuales
- `generate_utm_suggestions.py` - Sugerencias de UTMs

### 🔧 Optimización y Mantenimiento
- `optimize_csv_master.py` - Optimización del CSV Master
- `auto_fix_gaps.py` - Auto-fix de gaps SVG ↔ CSV
- `create_version_control.py` - Sistema de versionado

### 📊 Reporting
- `generate_executive_summary.py` - Resumen ejecutivo
- `generate_comprehensive_report.py` - Reporte comprehensivo
- `generate_collaboration_report.py` - Reporte de colaboración
- `generate_performance_report.py` - Reporte de performance

### 📤 Exportación
- `export_to_excel.py` - Exportación a Excel con formato
- `generate_assets_dashboard_html.py` - Dashboard visual interactivo
- `unified_dashboard.py` - Dashboard unificado completo

### 📧 Notificaciones
- `send_notifications.py` - Notificaciones multi-canal (Slack, Email, Teams)

### 🌐 Integraciones
- `multi_platform_integration.py` - Integración multi-plataforma
- `generate_api_docs.py` - Documentación de APIs
- `sync_to_linkedin.py` - Sync con LinkedIn Campaign Manager

### 💾 Backup y Restore
- `backup_restore_system.py` - Sistema de backup y restore

### 📊 Métricas Personalizadas
- `generate_custom_metrics.py` - Generador de métricas personalizadas

### ⚙️ Automatización
- `batch_process_creatives.py` - Procesamiento batch con presets
- `workflow_automation.py` - Automatización de workflows
- `generate_utm_urls_from_csv.py` - Generación de URLs con UTMs
- `automate_campaign_setup.py` - Automatización de setup de campañas

### 🔧 Utilidades
- `generate_custom_script.py` - Generador de scripts personalizados
- `generate_utm_gaps_report.py` - Reporte de gaps SVG-CSV

### 📅 Reportes Programados
- `generate_scheduled_reports.py` - Generador de reportes programados (diario/semanal/mensual)
- `compare_versions.py` - Comparador de versiones de creativos
- `cleanup_system.py` - Limpieza y mantenimiento del sistema
- `market_intelligence.py` - Market intelligence y análisis competitivo

### 📊 Analytics Avanzados
- `generate_asset_analytics.py` - Analytics avanzados de assets y patrones de uso
- `auto_generate_variants.py` - Generador automático de variantes de creativos exitosos
- `predictive_insights.py` - Insights predictivos y recomendaciones inteligentes
- `generate_competitor_analysis.py` - Análisis competitivo y benchmarking vs. industria

## 🚀 Workflows Recomendados

### Diario
```bash
python3 tools/quick_status.py
python3 tools/continuous_health_monitor.py --iterations 1
```

### Semanal
```bash
python3 tools/workflow_automation.py weekly
python3 tools/unified_dashboard.py
```

### Mensual
```bash
python3 tools/workflow_automation.py monthly
python3 tools/generate_comprehensive_report.py
python3 tools/market_intelligence.py
```

### Mantenimiento
```bash
# Limpieza del sistema (dry-run)
python3 tools/cleanup_system.py

# Aplicar limpieza
python3 tools/cleanup_system.py --apply

# Comparar versiones
python3 tools/compare_versions.py

# Generar reportes programados
python3 tools/generate_scheduled_reports.py weekly
```

### Pre-Campaña
```bash
python3 tools/workflow_automation.py pre_campaign
python3 tools/backup_restore_system.py create "Antes de campaña"
```

### Post-Campaña
```bash
python3 tools/workflow_automation.py post_campaign
python3 tools/generate_executive_summary.py
```

## 📦 Instalación de Dependencias

```bash
# Dependencias básicas
pip install requests python-dotenv

# Para Excel export
pip install openpyxl

# Para APIs (opcionales)
pip install facebook-business google-ads twitter-ads google-analytics-data
```

## 🎯 Quick Start

```bash
# 1. Ver status rápido
python3 tools/quick_status.py

# 2. Análisis completo
python3 tools/batch_process_creatives.py full

# 3. Ver dashboard
open exports/unified_dashboard.html

# 4. Ver recomendaciones
python3 tools/intelligent_recommendations.py
```

---

*Para documentación detallada de cada herramienta, consulta `26_ADVANCED_AUTOMATION_WORKFLOWS.md`*

