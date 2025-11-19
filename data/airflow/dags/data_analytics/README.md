# 📈 Data & Analytics DAGs

DAGs relacionados con ETL, calidad de datos, KPIs, sincronización de datos, integraciones y machine learning.

## Estructura

### 🔄 **etl/** - Procesos ETL
- **Ejemplos**: `etl_example.py`, `etl_improved.py`, `etl_downstream_example.py`
- **Consumidores**: `etl_consumer.py`, `post_etl_consumer.py`
- **Configuración**: `etl_config_constants.py`
- **Utilidades**: `etl_utils.py`
- **Mantenimiento**: `etl_maintenance.py`
- **Optimizaciones**: `etl_optimizations.py`
- **Integración de datos**: `data_integration_etl.py`
- **Ingesta por lotes**: `batch_ingestion_dag.py`
- **Productor de fuentes**: `source_producer.py`
- **Reportes post-ETL**: `post_etl_report.py`
- **Tests**: `test_etl_example.py`, `test_etl_utils.py`
- **Documentación**: 
  - `ETL_IMPROVEMENTS.md`
  - `INDEX_ETL_IMPROVED.md`
  - `README_DATA_INTEGRATION_ETL.md`
  - `README_ETL_IMPROVED.md`

### ✅ **data_quality/** - Calidad de Datos
- **Monitoreo**: `data_quality_monitoring.py`
- **Tests**: `test_dq_helper.py`

### 📊 **kpi/** - KPIs y Reportes
- **Agregación diaria**: `kpi_aggregate_daily.py`
- **Chequeos de salud DQ**: `kpi_dq_health_checks.py`
- **Rendimiento de queries**: `kpi_query_performance.py`
- **Actualización de materializados**: `kpi_refresh_materialized.py`, `refresh_kpi_materialized.py`
- **Reportes**: `kpi_reports.py`, `kpi_reports_weekly.py`, `kpi_reports_monthly.py`

### 🔄 **data_sync/** - Sincronización de Datos
- **Sincronización unificada**: `data_sync_unified.py`
- **Sincronización bidireccional CRM**: `crm_bidirectional_sync.py`

### 🔌 **airbyte/** - Integraciones Airbyte
- **Sincronización**: `airbyte_sync.py`
- **Ejemplos avanzados**: `airbyte_advanced_examples.py`
- **Documentación**: `README_AIRBYTE.md`

### 🤖 **ml/** - Machine Learning
- **Entrenamiento**: `mlflow_train.py`
- **Limpieza**: `mlflow_cleanup.py`

## Estadísticas
- **Total de DAGs**: 31 archivos Python
- **Documentación**: 5 archivos Markdown

