# 🎯 Sistema de Automatización de Calificación de Leads y Seguimiento de Ventas

Sistema completo y automatizado para gestionar todo el ciclo de ventas desde la calificación de leads hasta el cierre.

## 🚀 Inicio Rápido

**Para empezar en 5 minutos:**
👉 [Quick Start Guide](QUICK_START_SALES.md)

**Para entender el sistema completo:**
👉 [README Principal](README_SALES_AUTOMATION.md)

**Para resumen ejecutivo:**
👉 [Executive Summary](EXECUTIVE_SUMMARY.md)

## 📚 Documentación Completa

| Documento | Descripción |
|-----------|-------------|
| [Quick Start](QUICK_START_SALES.md) | Guía de inicio rápido (5 min) |
| [README Principal](README_SALES_AUTOMATION.md) | Documentación completa del sistema |
| [Executive Summary](EXECUTIVE_SUMMARY.md) | Resumen ejecutivo para stakeholders |
| [Best Practices](BEST_PRACTICES.md) | Mejores prácticas y recomendaciones |
| [Queries Guide](README_SALES_QUERIES.md) | Guía de queries SQL y vistas |
| [Migration Guide](MIGRATION_GUIDE.md) | Guía de actualización de versiones |
| [Index](INDEX_SALES_SYSTEM.md) | Índice completo de toda la documentación |
| [Changelog](CHANGELOG.md) | Historial de cambios y versiones |

## 🎯 Componentes Principales

### 🔄 Automatización (8 DAGs)
- **Lead Scoring** - Calcula scores automáticamente
- **Follow-up** - Gestiona seguimiento y tareas
- **Routing** - Asignación inteligente de leads
- **Alerts** - Alertas proactivas
- **ML Predictions** - Predicciones con ML
- **Timing Optimizer** - Optimización de timing
- **Analytics** - Reportes automáticos
- **CRM Sync** - Sincronización con CRM

### 🗄️ Base de Datos
- **Schema completo** - 6 tablas principales
- **Queries optimizadas** - 5 vistas y 3 funciones
- **Índices** - Para máximo performance

### 🛠️ Utilidades
- **Campaign Manager** - Gestión de campañas
- **Insights CLI** - Análisis desde línea de comandos
- **Validation** - Validación del sistema
- **Health Check** - Monitoreo de salud
- **Setup Script** - Instalación automatizada
- **Monitor Script** - Monitoreo continuo

## 📊 Características Principales

✅ **Scoring Automático** - Calcula scores basado en múltiples factores  
✅ **Asignación Inteligente** - Routing basado en carga y performance  
✅ **Seguimiento Automático** - Tareas y campañas automatizadas  
✅ **Predicciones ML** - Probabilidad de cierre y valor esperado  
✅ **Optimización Continua** - Ajusta timing basado en datos  
✅ **Alertas Proactivas** - Detecta situaciones críticas  
✅ **Reportes Automáticos** - Analytics semanales/mensuales  
✅ **Integración CRM** - Sincronización con HubSpot/Salesforce  

## 🎓 Flujo Recomendado

1. **Inicio**: Leer [Quick Start](QUICK_START_SALES.md)
2. **Setup**: Ejecutar `setup_sales_system.sh`
3. **Configuración**: Seguir [Best Practices](BEST_PRACTICES.md)
4. **Operación**: Usar scripts de monitoreo y validación
5. **Optimización**: Analizar métricas y ajustar

## 📈 Métricas Clave

- **Pipeline Value**: Valor total ponderado de oportunidades
- **Conversion Rate**: % de leads que se convierten
- **Win Rate**: % de deals ganados
- **Time to Close**: Días promedio hasta cierre
- **Task Completion**: % de tareas completadas a tiempo

## 🔧 Configuración Rápida

```bash
# 1. Setup automatizado
./scripts/setup_sales_system.sh

# 2. Validar sistema
python scripts/validate_sales_system.py --db "..."

# 3. Health check
python scripts/sales_health_check.py --db "..."

# 4. Monitoreo continuo
SALES_DB_CONN="..." ./scripts/monitor_sales_system.sh
```

## 📁 Archivos Principales

### Schema y Queries
- `sales_tracking_schema.sql` - Schema principal
- `sales_queries_optimized.sql` - Queries optimizadas

### DAGs
- `lead_scoring_automation.py`
- `sales_followup_automation.py`
- `sales_intelligent_routing.py`
- `sales_alerts_intelligent.py`
- `sales_ml_predictions.py`
- `sales_timing_optimizer.py`
- `sales_analytics_reports.py`
- `sales_crm_sync.py`

### Scripts
- `setup_sales_system.sh` - Setup automatizado
- `manage_sales_campaigns.py` - Gestión de campañas
- `sales_insights_cli.py` - Análisis CLI
- `validate_sales_system.py` - Validación
- `sales_health_check.py` - Health check
- `monitor_sales_system.sh` - Monitoreo continuo

## 🆘 Soporte

### Problemas Comunes
Ver sección Troubleshooting en [README Principal](README_SALES_AUTOMATION.md)

### Validación
```bash
python scripts/validate_sales_system.py --db "..." --all
```

### Health Check
```bash
python scripts/sales_health_check.py --db "..."
```

## 📝 Ejemplos

### Campañas
Ver ejemplos en `/data/db/examples/campaign_examples.json`

### Configuración Producción
Ver ejemplo en `/data/db/examples/production_config.yaml`

## 🎯 Estado del Sistema

✅ **Completo y listo para producción**  
✅ **Totalmente documentado**  
✅ **Validación y monitoreo incluidos**  
✅ **Optimizado para performance**  
✅ **Escalable y mantenible**  

---

**Sistema desarrollado para maximizar conversión y eficiencia de ventas** 🚀
