# 📚 Índice Completo - Sistema de Automatización de Ventas

Índice completo de toda la documentación y recursos del sistema.

## 🚀 Inicio Rápido

1. **[Quick Start Guide](QUICK_START_SALES.md)** - Comienza aquí para configurar el sistema
2. **[README Principal](README_SALES_AUTOMATION.md)** - Documentación completa del sistema

## 📋 Componentes Principales

### 🗄️ Base de Datos

- **[Schema Principal](sales_tracking_schema.sql)** - Tablas, funciones y triggers
- **[Queries Optimizadas](sales_queries_optimized.sql)** - Vistas, funciones y índices
- **[Documentación de Queries](README_SALES_QUERIES.md)** - Guía de uso de queries

### 🔄 DAGs de Airflow

#### Core Automation
- **Lead Scoring** (`lead_scoring_automation.py`) - Calcula scores automáticamente
- **Sales Follow-up** (`sales_followup_automation.py`) - Gestiona seguimiento y tareas
- **Sales Analytics** (`sales_analytics_reports.py`) - Reportes automáticos
- **CRM Sync** (`sales_crm_sync.py`) - Sincronización con CRM

#### Inteligencia Avanzada
- **Intelligent Routing** (`sales_intelligent_routing.py`) - Asignación inteligente
- **Intelligent Alerts** (`sales_alerts_intelligent.py`) - Alertas proactivas
- **ML Predictions** (`sales_ml_predictions.py`) - Predicciones ML
- **Timing Optimizer** (`sales_timing_optimizer.py`) - Optimización de timing

### 🛠️ Scripts de Utilidad

- **Campaign Manager** (`manage_sales_campaigns.py`) - Gestión de campañas
- **Insights CLI** (`sales_insights_cli.py`) - Análisis desde CLI
- **Validation** (`validate_sales_system.py`) - Validación del sistema
- **Health Check** (`sales_health_check.py`) - Monitoreo de salud

## 📖 Documentación

### Guías

- **[README Principal](README_SALES_AUTOMATION.md)** - Documentación completa
- **[Mejores Prácticas](BEST_PRACTICES.md)** - Guía de mejores prácticas
  - Schema de base de datos
  - Configuración de DAGs
  - Cálculo de scores
  - Campañas automatizadas
  - Troubleshooting

- **[Quick Start](QUICK_START_SALES.md)** - Guía de inicio rápido
  - Instalación paso a paso
  - Configuración mínima
  - Primeras pruebas
  - Checklist de inicio

- **[Queries](README_SALES_QUERIES.md)** - Guía de queries SQL
  - Vistas disponibles
  - Funciones SQL
  - Ejemplos de uso
  - Optimizaciones

- **[Migración](MIGRATION_GUIDE.md)** - Guía de actualización
  - Procesos de migración
  - Backup y rollback
  - Validación post-migración

## 🎯 Casos de Uso

### Configuración Inicial
1. Leer [Quick Start](QUICK_START_SALES.md)
2. Ejecutar schema SQL
3. Configurar vendedores
4. Configurar DAGs en Airflow
5. Crear primera campaña
6. Validar sistema

### Operación Diaria
- Monitorear health check
- Revisar alertas en Slack
- Analizar reportes semanales
- Gestionar campañas desde CLI

### Análisis y Reportes
- Usar vistas SQL para dashboards
- Ejecutar insights CLI
- Revisar métricas en materialized views
- Analizar embudo de conversión

### Troubleshooting
- Validar sistema con script
- Revisar logs de DAGs
- Consultar queries de diagnóstico
- Verificar integridad de datos

## 📊 Métricas y KPIs

### Pipeline Metrics
- Total de leads calificados
- Pipeline value (ponderado)
- Conversión por etapa
- Tiempo promedio en cada etapa

### Performance Metrics
- Win rate por vendedor
- Revenue por fuente
- Tasa de conversión
- Tiempo promedio a cierre

### Automation Metrics
- Leads calificados automáticamente
- Tareas creadas automáticamente
- Campañas ejecutadas
- Acciones completadas

## 🔧 Configuración

### Parámetros Principales

#### Lead Scoring
- `min_score_to_qualify`: 50 (default)
- `max_leads_per_run`: 500
- `enable_ml_scoring`: false

#### Follow-up
- `auto_assign_enabled`: true
- `enable_auto_tasks`: true
- `default_followup_days`: 3

#### Routing
- `max_active_leads_per_rep`: 50
- `enable_load_balancing`: true

#### Alerts
- `high_value_threshold`: 10000
- `stale_lead_days`: 7

## 📁 Estructura de Archivos

```
data/
├── db/
│   ├── sales_tracking_schema.sql          # Schema principal
│   ├── sales_queries_optimized.sql        # Queries optimizadas
│   ├── README_SALES_AUTOMATION.md         # Documentación principal
│   ├── README_SALES_QUERIES.md            # Documentación de queries
│   ├── QUICK_START_SALES.md                # Guía rápida
│   ├── MIGRATION_GUIDE.md                 # Guía de migración
│   └── INDEX_SALES_SYSTEM.md              # Este archivo
│
├── airflow/
│   └── dags/
│       ├── lead_scoring_automation.py
│       ├── sales_followup_automation.py
│       ├── sales_analytics_reports.py
│       ├── sales_crm_sync.py
│       ├── sales_intelligent_routing.py
│       ├── sales_alerts_intelligent.py
│       ├── sales_ml_predictions.py
│       └── sales_timing_optimizer.py
│
└── scripts/
    ├── manage_sales_campaigns.py
    ├── sales_insights_cli.py
    ├── validate_sales_system.py
    └── sales_health_check.py
```

## 🎓 Flujo de Aprendizaje Recomendado

1. **Inicio**: Leer [Quick Start](QUICK_START_SALES.md)
2. **Conceptos**: Leer secciones principales de [README](README_SALES_AUTOMATION.md)
3. **Práctica**: Configurar sistema básico
4. **Avanzado**: Explorar queries y vistas optimizadas
5. **Optimización**: Configurar ML y timing optimizer
6. **Mantenimiento**: Usar scripts de validación y health check

## 🔗 Integraciones

### Sistemas Complementarios
- **Lead Nurturing** - Sistema de nutrición de leads fríos
- **CRM** - HubSpot/Salesforce (sincronización)
- **Email** - Webhook de envío de emails
- **Slack** - Notificaciones y alertas

### APIs Externas
- Modelo ML para predicciones (opcional)
- API de llamadas (opcional)
- Task manager externo (opcional)

## 📈 Roadmap

### ✅ Completado
- [x] Sistema de scoring automático
- [x] Seguimiento automatizado
- [x] Routing inteligente
- [x] Alertas proactivas
- [x] Reportes automáticos
- [x] Integración con CRM
- [x] Predicciones ML
- [x] Optimización de timing
- [x] Queries optimizadas
- [x] Scripts de utilidad

### 🔄 En Desarrollo
- [ ] Dashboard web en tiempo real
- [ ] A/B testing de campañas
- [ ] Soporte WhatsApp/SMS
- [ ] Integración con calendario

## 🆘 Soporte

### Problemas Comunes
Ver sección Troubleshooting en [README](README_SALES_AUTOMATION.md)

### Validación
```bash
python scripts/validate_sales_system.py --db "..." --all
```

### Health Check
```bash
python scripts/sales_health_check.py --db "..."
```

### Logs
- Revisar logs de Airflow para DAGs
- Consultar logs de PostgreSQL para queries
- Verificar métricas en materialized views

## 📝 Notas Finales

Este sistema está diseñado para ser:
- **Modular**: Cada componente funciona independientemente
- **Escalable**: Maneja grandes volúmenes de leads
- **Inteligente**: Usa ML y análisis para optimizar
- **Robusto**: Validación y monitoreo integrados
- **Documentado**: Guías completas para todos los casos

Para más información, consulta la documentación específica de cada componente.

