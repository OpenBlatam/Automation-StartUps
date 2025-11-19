# DAG de Integración de Datos ETL

## Descripción

Este DAG automatiza la integración de datos entre múltiples sistemas:

## Mejoras Implementadas

### ✨ Funcionalidades Avanzadas

1. **Métricas y Observabilidad**
   - Tracking completo con Airflow Stats
   - Métricas de duración, éxito y errores por etapa
   - Tags para segmentación (crm_type, source, etc.)
   - Gauge métricas para contadores y porcentajes

2. **Manejo de Errores Robusto**
   - Retry automático con exponential backoff
   - Jitter aleatorio para evitar thundering herd
   - Retry específico por tipo de excepción
   - Logging estructurado con contexto

3. **Performance y Optimización**
   - Progress tracking para operaciones largas
   - Batch processing optimizado con progreso
   - Timeouts configurables por tarea
   - Connection pooling para PostgreSQL

4. **Context Managers**
   - `_track_metric()` para tracking automático de métricas
   - Captura de duración y estados de éxito/error
   - Manejo de errores en métricas sin afectar ejecución

5. **Utility Functions**
   - `_retry_with_exponential_backoff()` - Retry avanzado con jitter
   - `_track_metric()` - Context manager para tracking automático
   - `_log_progress()` - Logging de progreso para loops largos
   - Funciones reutilizables y bien documentadas

6. **Health Checks**
   - Verificación pre-vuelo de sistemas y dependencias
   - Validación de configuraciones (CRM, Sheets, PostgreSQL)
   - Circuit breaker status check
   - Falla rápida si hay problemas críticos

7. **Dead Letter Queue (DLQ)**
   - Tabla `data_integration_dlq` para registros fallidos
   - Guardado automático de registros con errores
   - Tracking de reintentos y resolución
   - Métricas de registros en DLQ

8. **Circuit Breaker Pattern**
   - Protección contra fallos en cascada
   - Threshold configurable (default: 5 fallos)
   - Reset automático después de período configurable
   - Integración con callbacks de DAG

9. **Rate Limiting**
   - Clase `RateLimiter` para control de llamadas
   - Configurable por operación
   - Prevención de throttling de APIs externas

10. **Caché Inteligente**
    - Caché en memoria con TTL configurable
    - Generación automática de claves
    - Limpieza automática de entradas expiradas
    - Estadísticas de hits/misses

11. **Data Profiling**
    - Análisis automático de estructura de datos
    - Detección de tipos de datos
    - Cálculo de completitud por campo
    - Identificación de valores únicos
    - Métricas de calidad de datos

12. **Checkpointing**
    - Guardado automático de estado de procesamiento
    - Recuperación desde último checkpoint
    - Tabla `data_integration_checkpoints` para persistencia
    - Procesamiento resumible en caso de fallos

13. **Procesamiento Paralelo**
    - Procesamiento de chunks en paralelo usando ThreadPoolExecutor
    - Configurable por número de workers
    - Mejora significativa de rendimiento para grandes volúmenes
    - Fallback automático a procesamiento secuencial si es necesario

14. **Procesamiento Incremental**
    - Tracking de última sincronización por fuente
    - Tabla `data_integration_sync_log` para persistencia
    - Sincronización solo de datos nuevos/modificados
    - Reducción de carga y tiempo de procesamiento

15. **Generación de Reportes Ejecutivos**
    - Reportes automáticos con métricas de todas las etapas
    - Análisis de calidad de datos
    - Recomendaciones automáticas basadas en hallazgos
    - Persistencia en tabla `data_integration_reports`

16. **Validación de Esquemas Robusta**
    - Sistema de validación basado en reglas configurables
    - Validación de tipos, rangos, patrones regex
    - Validadores personalizados
    - Soporte para campos requeridos/opcionales

17. **Conversión de Monedas**
    - Normalización automática a moneda objetivo
    - Soporte para múltiples monedas (USD, EUR, GBP, MXN, CAD, AUD)
    - Preservación de valores originales
    - Tracking de conversiones realizadas

18. **Detección de Outliers**
    - Detección estadística de valores atípicos
    - Métodos IQR y Z-Score
    - Análisis de distribución estadística
    - Alertas automáticas para outliers significativos

19. **Análisis de Tendencias Temporales**
    - Análisis de tendencias por día
    - Cálculo de tasas de crecimiento
    - Identificación de patrones (increasing/decreasing/stable)
    - Estadísticas diarias agregadas

20. **Sistema de Auditoría Completo**
    - Logging de todas las operaciones importantes
    - Tabla `data_integration_audit_log` para persistencia
    - Tracking de acciones, entidades y usuarios
    - Índices optimizados para consultas de auditoría

21. **Data Lineage Tracking**
    - Rastreo completo del origen y transformación de datos
    - Tabla `data_integration_lineage` para persistencia
    - Tracking de pasos de transformación
    - Identificación única de lineage por registro

22. **Deduplicación de Datos**
    - Detección automática de registros duplicados
    - Múltiples estrategias (latest, first, most_complete)
    - Campos configurables para deduplicación
    - Estadísticas de duplicados detectados

23. **Enriquecimiento de Datos**
    - Enriquecimiento automático con información adicional
    - Extracción de dominio de email
    - Detección de emails corporativos
    - Formateo de nombres y montos
    - Versión de enriquecimiento trackeable

24. **Versionado de Datos**
    - Creación automática de versiones de datos
    - Tabla `data_integration_versions` para persistencia
    - Metadata completa de cada versión
    - Tracking de historial de versiones

25. **Compresión de Datos**
    - Compresión automática usando gzip
    - Serialización eficiente para almacenamiento
    - Reducción significativa de uso de memoria
    - Soporte para descompresión automática

26. **Particionamiento de Tablas**
    - Particionamiento automático por fecha (mensual)
    - Mejora significativa de rendimiento en queries
    - Creación automática de particiones futuras
    - Optimización de mantenimiento de tablas grandes

27. **Backup Automático**
    - Backup automático antes de operaciones críticas
    - Backup de últimos 7 días por defecto
    - Índices optimizados en tablas de backup
    - Preparación para rollback rápido

28. **Rollback Automático**
    - Rollback automático en caso de alta tasa de errores (>50%)
    - Restauración desde backup creado previamente
    - Protección contra corrupción de datos
    - Configurable con umbral de errores

29. **Archivado de Datos**
    - Archivado automático de datos antiguos
    - Configurable por días de retención (default: 90 días)
    - Tabla de archivo separada para datos históricos
    - Limpieza automática de tabla principal

30. **Reconciliación de Datos**
    - Matching inteligente entre diferentes fuentes
    - Detección automática de registros duplicados entre fuentes
    - Cálculo de similitud usando SequenceMatcher
    - Detección de conflictos entre fuentes
    - Threshold configurable de similitud (default: 0.85)

31. **Detección de PII**
    - Detección automática de información personal identificable
    - Soporte para email, teléfono, SSN, tarjetas de crédito, IP
    - Tracking de campos PII encontrados
    - Estadísticas de PII por registro

32. **Enmascaramiento de PII**
    - Enmascaramiento automático de datos sensibles
    - Patrones de enmascaramiento para emails y teléfonos
    - Preservación de formato para legibilidad
    - Timestamp de enmascaramiento

33. **Tracking de Costos**
    - Cálculo automático de costos estimados por operación
    - Costos por segundo de compute, storage, network
    - Costo por registro procesado
    - Persistencia en base de datos para análisis histórico
    - Integración con DAG run ID

34. **Estrategias de Retry Inteligentes**
    - Detección automática de tipo de error
    - Retry solo para errores temporales (timeout, network, rate limit)
    - No retry para errores permanentes (404, auth, syntax)
    - Exponential backoff configurable
    - Máximo de reintentos configurable

35. **Scoring de Calidad de Datos**
    - Score de calidad por registro (0-100)
    - Evaluación en 4 dimensiones: Completeness, Validity, Consistency, Accuracy
    - Niveles de calidad: excellent, good, fair, poor, critical
    - Score promedio del dataset
    - Distribución de calidad por niveles
    - Deducciones detalladas por aspecto

36. **Reglas Automáticas de Calidad**
    - Motor de reglas configurable
    - Reglas por defecto: email requerido, formato válido, montos no negativos, etc.
    - Severidad configurable (warning, error, critical)
    - Auto-fix opcional para reglas
    - Pasos por registro y dataset completo
    - Tracking de violaciones por regla

37. **Alertas Inteligentes**
    - Sistema de alertas basado en reglas configurables
    - Reglas por defecto: alta tasa de errores, calidad baja, conflictos de reconciliación, PII no enmascarado, validación baja
    - Severidad configurable (warning, error, critical)
    - Notificaciones automáticas a Slack y/o Email
    - Templates de mensajes personalizables
    - Evaluación automática al final del pipeline

38. **Monitoreo en Tiempo Real**
    - Tracking de métricas de operaciones en tiempo real
    - Health score del pipeline (0-100)
    - Evaluación de componentes: Extracción, Transformación, Validación, Carga
    - Estados de salud: excellent, good, fair, poor, critical
    - Persistencia en base de datos para análisis histórico
    - Integración con DAG run ID

39. **Detección de Deriva de Datos (Data Drift)**
    - Comparación estadística con baseline histórico
    - Detección de cambios en distribuciones numéricas y categóricas
    - Creación automática de baseline desde datos actuales
    - Persistencia de baseline en base de datos
    - Score de deriva por campo y general
    - Alertas automáticas cuando se detecta deriva significativa

40. **Detección Avanzada de Anomalías**
    - Múltiples métodos: Statistical (Z-score, IQR), Isolation Forest, Clustering
    - Detección de outliers en campos numéricos
    - Detección de valores categóricos raros
    - Consolidación de anomalías por registro
    - Métricas de tasa de anomalías
    - Identificación de razones de anomalía

41. **Auto-tuning de Rendimiento**
    - Análisis automático de métricas históricas de ejecución
    - Recomendaciones inteligentes para optimizar parámetros
    - Ajuste automático de batch_size, max_workers, chunk_size
    - Score de optimización (0-100)
    - Tracking de throughput, tiempo de ejecución, tasa de errores
    - Persistencia de métricas para análisis continuo

42. **Catálogo de Datos**
    - Registro automático de tablas y esquemas
    - Metadatos enriquecidos (descripción, tags, owner)
    - Búsqueda y descubrimiento de datos
    - Versionado de esquemas
    - Integración con herramientas de gobernanza

43. **Contratos de Datos**
    - Definición de expectativas sobre calidad de datos
    - Validación automática contra contratos
    - Reglas configurables: not_null, unique, range, custom
    - Severidad configurable (error, warning)
    - Tracking de violaciones en base de datos
    - Alertas automáticas por violaciones

44. **Pruebas Automatizadas**
    - Suite completa de pruebas end-to-end
    - Pruebas de completitud, integridad, calidad, consistencia
    - Pruebas de flujo end-to-end
    - Persistencia de resultados en base de datos
    - Reportes de estado (passed, failed, partial)
    - Integración con CI/CD

- **CRM** (Salesforce/Pipedrive): Contactos, leads, oportunidades
- **Google Sheets**: Datos manuales, reportes, configuraciones
- **Sistema de Facturación**: Facturas, pagos, transacciones

El proceso incluye:
1. ✅ Extracción de datos de todas las fuentes
2. ✅ Transformación y normalización
3. ✅ Validación de calidad de datos
4. ✅ Carga en data warehouse (PostgreSQL)
5. ✅ Detección de inconsistencias
6. ✅ Alertas automáticas

## Configuración

### Variables de Entorno Requeridas

```bash
# PostgreSQL
POSTGRES_CONN_ID=postgres_default

# CRM - Salesforce
SALESFORCE_USERNAME=user@example.com
SALESFORCE_PASSWORD=password
SALESFORCE_SECURITY_TOKEN=token
SALESFORCE_CLIENT_ID=client_id
SALESFORCE_CLIENT_SECRET=client_secret

# CRM - Pipedrive
PIPEDRIVE_API_TOKEN=api_token
PIPEDRIVE_COMPANY_DOMAIN=company_domain

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=spreadsheet_id

# Alertas
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DATA_ALERT_EMAIL=team@example.com
```

### Parámetros del DAG

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `postgres_conn_id` | string | `postgres_default` | ID de conexión PostgreSQL |
| `crm_type` | string | `salesforce` | Tipo de CRM (`salesforce` o `pipedrive`) |
| `crm_config` | string | `{}` | Configuración del CRM en JSON |
| `sheets_spreadsheet_id` | string | `` | ID del Google Spreadsheet |
| `sheets_credentials_json` | string | `{}` | Credenciales de Google Service Account (JSON) |
| `sheets_range` | string | `Sheet1!A:Z` | Rango de celdas a extraer |
| `billing_source` | string | `database` | Fuente de facturación (`database` o `api`) |
| `enable_validation` | boolean | `true` | Habilitar validación de datos |
| `enable_alerts` | boolean | `true` | Habilitar alertas |
| `enable_dlq` | boolean | `true` | Habilitar Dead Letter Queue |
| `enable_circuit_breaker` | boolean | `true` | Habilitar circuit breaker |
| `enable_rate_limiting` | boolean | `false` | Habilitar rate limiting |
| `enable_cache` | boolean | `true` | Habilitar caché |
| `enable_checkpointing` | boolean | `true` | Habilitar checkpointing |
| `enable_data_profiling` | boolean | `true` | Habilitar data profiling |
| `enable_parallel_processing` | boolean | `true` | Habilitar procesamiento paralelo |
| `enable_incremental` | boolean | `false` | Habilitar procesamiento incremental |
| `enable_reports` | boolean | `true` | Habilitar generación de reportes |
| `enable_schema_validation` | boolean | `true` | Habilitar validación de esquemas robusta |
| `enable_currency_conversion` | boolean | `false` | Habilitar conversión de monedas |
| `target_currency` | string | `USD` | Moneda objetivo para conversión |
| `enable_outlier_detection` | boolean | `true` | Habilitar detección de outliers |
| `enable_temporal_analysis` | boolean | `true` | Habilitar análisis de tendencias temporales |
| `enable_audit_logging` | boolean | `true` | Habilitar logging de auditoría |
| `enable_data_lineage` | boolean | `true` | Habilitar tracking de data lineage |
| `enable_deduplication` | boolean | `true` | Habilitar deduplicación de datos |
| `deduplication_fields` | string | `email,customer_id` | Campos para deduplicación (separados por coma) |
| `deduplication_strategy` | string | `latest` | Estrategia de deduplicación (`latest`, `first`, `most_complete`) |
| `enable_data_enrichment` | boolean | `true` | Habilitar enriquecimiento de datos |
| `enable_data_versioning` | boolean | `false` | Habilitar versionado de datos |
| `enable_table_partitioning` | boolean | `false` | Habilitar particionamiento de tablas |
| `enable_backup` | boolean | `true` | Habilitar backup automático |
| `enable_auto_rollback` | boolean | `false` | Habilitar rollback automático en errores |
| `enable_data_archiving` | boolean | `false` | Habilitar archivado automático de datos |
| `archive_older_than_days` | integer | `90` | Días de retención antes de archivar |
| `enable_data_reconciliation` | boolean | `true` | Habilitar reconciliación de datos entre fuentes |
| `reconciliation_threshold` | number | `0.85` | Umbral de similitud para matching (0.5-1.0) |
| `enable_pii_detection` | boolean | `true` | Habilitar detección de información PII |
| `enable_pii_masking` | boolean | `false` | Habilitar enmascaramiento de PII |
| `enable_cost_tracking` | boolean | `true` | Habilitar tracking de costos de operaciones |
| `enable_smart_retry` | boolean | `true` | Habilitar estrategias de retry inteligentes |
| `enable_quality_scoring` | boolean | `true` | Habilitar scoring de calidad de datos |
| `enable_quality_rules` | boolean | `true` | Habilitar reglas automáticas de calidad |
| `quality_threshold` | number | `60.0` | Score mínimo de calidad aceptable (0-100) |
| `enable_intelligent_alerting` | boolean | `true` | Habilitar alertas inteligentes |
| `enable_realtime_monitoring` | boolean | `true` | Habilitar monitoreo en tiempo real |
| `enable_data_drift_detection` | boolean | `true` | Habilitar detección de deriva de datos |
| `enable_advanced_anomaly_detection` | boolean | `true` | Habilitar detección avanzada de anomalías |
| `enable_performance_autotuning` | boolean | `true` | Habilitar auto-tuning de rendimiento |
| `drift_detection_threshold` | number | `0.05` | Umbral para detección de deriva (0.01-0.5) |
| `enable_data_catalog` | boolean | `true` | Habilitar registro en catálogo de datos |
| `enable_data_contracts` | boolean | `true` | Habilitar validación de contratos de datos |
| `enable_automated_testing` | boolean | `true` | Habilitar pruebas automatizadas |
| `dry_run` | boolean | `false` | Modo dry-run sin escribir cambios |
| `batch_size` | integer | `1000` | Tamaño de batch para carga |
| `circuit_breaker_threshold` | integer | `5` | Número de fallos antes de abrir circuit breaker |
| `circuit_breaker_reset_minutes` | integer | `15` | Minutos antes de resetear circuit breaker |
| `cache_ttl_seconds` | integer | `3600` | TTL del caché en segundos |
| `max_workers` | integer | `4` | Número máximo de workers para procesamiento paralelo |
| `chunk_size` | integer | `500` | Tamaño de chunk para procesamiento paralelo |

### Ejemplo de Configuración CRM

#### Salesforce
```json
{
  "username": "user@example.com",
  "password": "password",
  "security_token": "token",
  "client_id": "client_id",
  "client_secret": "client_secret",
  "sandbox": false
}
```

#### Pipedrive
```json
{
  "api_token": "api_token",
  "company_domain": "company_domain"
}
```

## Estructura del DAG

```
data_integration_etl
├── health_check
├── prepare_extraction
├── extract_data
│   ├── extract_crm_data
│   ├── extract_sheets_data
│   └── extract_billing_data
├── profile_data
├── transform_data
├── validate_data
├── load_to_warehouse
├── analyze_data_quality
├── detect_inconsistencies
├── generate_report
└── send_alerts
```

### Dead Letter Queue

Registros fallidos se guardan automáticamente en la tabla `data_integration_dlq`:

```sql
SELECT 
    source_type,
    COUNT(*) as failed_count,
    MAX(created_at) as last_failure
FROM data_integration_dlq
WHERE resolved_at IS NULL
GROUP BY source_type;
```

### Circuit Breaker

El circuit breaker se activa automáticamente después de múltiples fallos:
- Threshold: 5 fallos (configurable)
- Reset: 15 minutos (configurable)
- Se resetea automáticamente en éxito

### Checkpointing

El sistema guarda checkpoints automáticamente para permitir recuperación:
- Tabla: `data_integration_checkpoints`
- Checkpoints por etapa de procesamiento
- Recuperación automática desde último checkpoint

```sql
SELECT checkpoint_name, updated_at, data
FROM data_integration_checkpoints
ORDER BY updated_at DESC;
```

### Data Profiling

El sistema genera perfiles automáticos de los datos:
- Análisis de estructura por fuente
- Detección de tipos de datos
- Cálculo de completitud
- Identificación de campos requeridos

### Caché

Sistema de caché en memoria para optimizar rendimiento:
- TTL configurable (default: 1 hora)
- Limpieza automática de entradas expiradas
- Estadísticas de uso (hits/misses)

### Procesamiento Paralelo

El sistema procesa datos en paralelo cuando hay grandes volúmenes:
- División automática en chunks de tamaño configurable
- Procesamiento paralelo usando ThreadPoolExecutor
- Número de workers configurable (default: 4)
- Fallback automático a procesamiento secuencial

### Procesamiento Incremental

Soporte para sincronización incremental:
- Tracking de última sincronización por fuente
- Tabla `data_integration_sync_log` almacena timestamps
- Solo procesa datos nuevos/modificados desde última sync
- Reduce significativamente tiempo de procesamiento

```sql
SELECT source, last_sync_timestamp, records_processed, status
FROM data_integration_sync_log
ORDER BY last_sync_timestamp DESC;
```

### Reportes Ejecutivos

El sistema genera reportes automáticos con:
- Resumen de ejecución (extracción, transformación, validación, carga)
- Métricas de calidad de datos
- Análisis de inconsistencias por severidad
- Recomendaciones automáticas
- Persistencia diaria en tabla `data_integration_reports`

```sql
SELECT report_date, report_data->>'execution_summary' as summary
FROM data_integration_reports
ORDER BY report_date DESC
LIMIT 10;
```

### Validación de Esquemas Robusta

Sistema de validación basado en reglas configurables:
- Validación de tipos de datos
- Validación de rangos numéricos (min/max)
- Validación de patrones regex
- Lista de valores permitidos
- Validadores personalizados

### Conversión de Monedas

Normalización automática de monedas:
- Soporte para múltiples monedas (USD, EUR, GBP, MXN, CAD, AUD)
- Conversión a moneda objetivo configurable
- Preservación de valores originales
- Tracking de conversiones realizadas

### Detección de Outliers

Análisis estadístico de valores atípicos:
- Método IQR (Interquartile Range) por defecto
- Método Z-Score opcional
- Estadísticas de distribución (mean, median, stdev)
- Porcentaje de outliers detectados

### Análisis de Tendencias Temporales

Análisis de patrones temporales en los datos:
- Agrupación por día
- Cálculo de tasas de crecimiento
- Identificación de tendencias (increasing/decreasing/stable)
- Estadísticas diarias agregadas (total, count, average)

### Sistema de Auditoría

Logging completo de operaciones:
- Tabla `data_integration_audit_log` para persistencia
- Tracking de acciones, entidades, usuarios y timestamps
- Índices optimizados para consultas rápidas
- Integración con DAG run ID

```sql
SELECT action, entity_type, COUNT(*) as count, MAX(timestamp) as last_action
FROM data_integration_audit_log
WHERE dag_run_id = 'run_id_here'
GROUP BY action, entity_type
ORDER BY count DESC;
```

### Data Lineage Tracking

Rastreo completo del origen y transformación de datos:
- Tabla `data_integration_lineage` almacena información de lineage
- Tracking de pasos de transformación por registro
- Identificación única de lineage por registro
- Índices optimizados para consultas rápidas

```sql
SELECT lineage_id, source_type, source_id, transformation_steps
FROM data_integration_lineage
WHERE source_type = 'crm'
ORDER BY extracted_at DESC
LIMIT 10;
```

### Deduplicación de Datos

Detección y manejo automático de duplicados:
- Múltiples estrategias configurables:
  - `latest`: Mantiene el registro más reciente
  - `first`: Mantiene el primer registro encontrado
  - `most_complete`: Mantiene el registro con más campos completos
- Campos configurables para deduplicación
- Estadísticas de duplicados detectados

### Enriquecimiento de Datos

Enriquecimiento automático con información adicional:
- Extracción de dominio de email
- Detección de emails corporativos vs. personales
- Formateo de nombres completos
- Formateo de montos con moneda
- Versión de enriquecimiento trackeable

### Versionado de Datos

Sistema de versionado para tracking histórico:
- Tabla `data_integration_versions` almacena versiones
- Metadata completa de cada versión
- Integración con DAG run ID
- Consulta de versiones históricas

```sql
SELECT version_name, description, records_count, created_at
FROM data_integration_versions
ORDER BY created_at DESC
LIMIT 10;
```

### Compresión de Datos

Sistema de compresión para optimización de memoria:
- Compresión automática usando gzip
- Serialización eficiente con pickle
- Reducción significativa de uso de memoria
- Descompresión automática cuando es necesario

### Particionamiento de Tablas

Particionamiento automático para mejor rendimiento:
- Particionamiento mensual por fecha de creación
- Creación automática de particiones futuras
- Mejora significativa en queries de rangos de fecha
- Optimización de mantenimiento (VACUUM, análisis)

```sql
-- Ver particiones creadas
SELECT 
    schemaname, 
    tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'data_warehouse_integration%'
ORDER BY tablename;
```

### Backup Automático

Sistema de backup automático:
- Backup automático antes de operaciones críticas
- Backup de últimos 7 días por defecto
- Índices optimizados en tablas de backup
- Nombres de backup con timestamp para identificación única

```sql
-- Ver backups disponibles
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(table_name::regclass)) AS size,
    (SELECT COUNT(*) FROM information_schema.tables 
     WHERE table_name = t.table_name) as record_count
FROM information_schema.tables t
WHERE table_name LIKE 'data_warehouse_integration_backup%'
ORDER BY table_name DESC
LIMIT 10;
```

### Rollback Automático

Protección contra errores masivos:
- Rollback automático si tasa de errores > 50%
- Restauración desde backup previamente creado
- Protección contra corrupción de datos
- Umbral configurable de errores

### Archivado de Datos

Sistema de archivado automático:
- Archivado de datos más antiguos que N días (default: 90)
- Tabla de archivo separada (`data_warehouse_integration_archive`)
- Limpieza automática de tabla principal
- Preservación de datos históricos

```sql
-- Ver datos archivados
SELECT COUNT(*), MIN(created_at), MAX(created_at)
FROM data_warehouse_integration_archive;

-- Ver estadísticas de archivo
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as archived_count
FROM data_warehouse_integration_archive
GROUP BY month
ORDER BY month DESC;
```

### Reconciliación de Datos

Sistema de reconciliación entre múltiples fuentes:
- Matching inteligente usando similitud de strings
- Detección de registros duplicados entre fuentes
- Identificación de conflictos entre valores
- Threshold configurable de similitud

```python
# Ejemplo de uso en transformación
reconciliation_result = {
    "matched_pairs": 150,  # Pares de registros coincidentes
    "unmatched": 25,  # Registros sin match
    "conflicts": 10,  # Pares con valores conflictivos
    "total_records": 500
}
```

### Detección y Enmascaramiento de PII

Protección de datos personales:
- Detección automática de emails, teléfonos, SSN, tarjetas, IPs
- Enmascaramiento opcional con preservación de formato
- Tracking de campos PII encontrados
- Cumplimiento con regulaciones de privacidad

```sql
-- Ver estadísticas de PII
SELECT 
    COUNT(*) as total_records,
    COUNT(CASE WHEN pii_detection->>'has_pii' = 'true' THEN 1 END) as records_with_pii,
    jsonb_object_keys(pii_detection->'pii_details') as pii_fields
FROM data_warehouse_integration
WHERE pii_detection IS NOT NULL
GROUP BY pii_fields;
```

### Tracking de Costos

Monitoreo de costos de operaciones:
- Cálculo automático basado en duración y recursos
- Costos por tipo de recurso (compute, storage, network)
- Costo por registro procesado
- Historial completo en `data_integration_cost_tracking`

```sql
-- Ver costos por operación
SELECT 
    operation,
    SUM(estimated_cost_usd) as total_cost,
    AVG(cost_per_record) as avg_cost_per_record,
    COUNT(*) as executions
FROM data_integration_cost_tracking
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY operation
ORDER BY total_cost DESC;

-- Ver tendencia de costos
SELECT 
    DATE(timestamp) as date,
    operation,
    SUM(estimated_cost_usd) as daily_cost
FROM data_integration_cost_tracking
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY date, operation
ORDER BY date DESC, daily_cost DESC;
```

### Estrategias de Retry Inteligentes

Retry adaptativo basado en tipo de error:
- Retry automático para errores temporales (timeouts, network, rate limits)
- No retry para errores permanentes (404, auth, syntax errors)
- Exponential backoff con máximo configurable
- Reducción de intentos innecesarios

```python
# Ejemplo de uso
if SmartRetryStrategy.should_retry(exception, attempt, max_retries=3):
    delay = SmartRetryStrategy.calculate_delay(attempt, base_delay=1.0)
    time.sleep(delay)
    # Reintentar operación
```

### Scoring de Calidad de Datos

Sistema de scoring automático por registro:
- Score de 0-100 basado en 4 dimensiones
- **Completeness** (40 puntos): Campos obligatorios presentes
- **Validity** (30 puntos): Valores dentro de rangos esperados
- **Consistency** (20 puntos): Valores consistentes entre campos
- **Accuracy** (10 puntos): Formato y estructura correctos
- Niveles: excellent (≥90), good (≥75), fair (≥60), poor (≥40), critical (<40)

```sql
-- Ver distribución de calidad
SELECT 
    quality_score->>'quality_level' as quality_level,
    COUNT(*) as count,
    AVG((quality_score->>'score')::numeric) as avg_score
FROM data_warehouse_integration
WHERE quality_score IS NOT NULL
GROUP BY quality_level
ORDER BY avg_score DESC;

-- Ver registros con calidad baja
SELECT 
    source_id,
    email,
    quality_score->>'score' as score,
    quality_score->>'quality_level' as level,
    quality_score->'deductions' as deductions
FROM data_warehouse_integration
WHERE (quality_score->>'score')::numeric < 60
ORDER BY (quality_score->>'score')::numeric ASC
LIMIT 10;
```

### Reglas Automáticas de Calidad

Motor de reglas configurable:
- Reglas por defecto: email requerido, formato válido, montos no negativos, nombre completo, formato de customer_id
- Severidad configurable (warning, error, critical)
- Auto-fix opcional para reglas específicas
- Validación por registro y dataset completo
- Tracking de violaciones por regla

```python
# Ejemplo de resultado de reglas
quality_rules_result = {
    "total_records": 1000,
    "records_passed": 850,
    "records_failed": 150,
    "pass_rate": 85.0,
    "rule_violations": {
        "email_required": 50,
        "email_valid_format": 30,
        "amount_non_negative": 20,
        "name_completeness": 40,
        "customer_id_format": 10
    },
    "severity_counts": {
        "error": 80,
        "warning": 70
    }
}
```

### Alertas Inteligentes

Sistema de alertas basado en reglas configurables:
- Reglas por defecto: alta tasa de errores, calidad baja, conflictos de reconciliación, PII no enmascarado, tasa de validación baja
- Severidad configurable (warning, error, critical)
- Notificaciones automáticas a Slack y/o Email
- Templates de mensajes personalizables
- Evaluación automática al final del pipeline

```python
# Ejemplo de alerta generada
alert = {
    "rule": "high_error_rate",
    "severity": "critical",
    "message": "Alta tasa de errores: 15.50%",
    "timestamp": "2025-01-15T10:30:00Z",
    "notify_slack": True,
    "notify_email": True
}
```

### Monitoreo en Tiempo Real

Tracking de métricas y health score:
- Health score del pipeline (0-100)
- Evaluación de componentes: Extracción (30 pts), Transformación (25 pts), Validación (25 pts), Carga (20 pts)
- Estados de salud: excellent (≥90), good (≥75), fair (≥60), poor (≥40), critical (<40)
- Persistencia en `data_integration_metrics` para análisis histórico

```sql
-- Ver health scores históricos
SELECT 
    DATE(timestamp) as date,
    AVG(metric_value) as avg_health_score,
    COUNT(*) as executions
FROM data_integration_metrics
WHERE operation = 'pipeline_health' 
  AND metric_name = 'health_score'
  AND timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date
ORDER BY date DESC;

-- Ver componentes del health score
SELECT 
    metric_name,
    AVG(metric_value) as avg_score,
    MIN(metric_value) as min_score,
    MAX(metric_value) as max_score
FROM data_integration_metrics
WHERE operation = 'pipeline_health'
  AND timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY metric_name;
```

### Detección de Deriva de Datos

Sistema de detección de cambios en distribuciones de datos:
- Comparación estadística con baseline histórico
- Detección de cambios en distribuciones numéricas (medias, desviaciones)
- Detección de cambios en distribuciones categóricas
- Creación automática de baseline desde datos actuales
- Score de deriva por campo y general

```sql
-- Ver baseline de campos
SELECT 
    field_name,
    field_type,
    mean_value,
    std_value,
    created_at
FROM data_drift_baseline
ORDER BY created_at DESC;

-- Ver detecciones de deriva históricas
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as drift_detections,
    AVG(overall_drift_score) as avg_drift_score
FROM data_integration_reports
WHERE report_data->>'drift_detection' IS NOT NULL
  AND (report_data->'drift_detection'->>'drift_detected')::boolean = true
GROUP BY date
ORDER BY date DESC;
```

### Detección Avanzada de Anomalías

Múltiples métodos de detección:
- **Statistical**: Z-score y IQR para campos numéricos
- **Isolation Forest**: Detección basada en distancia
- **Clustering**: Valores categóricos raros

```python
# Ejemplo de resultado
anomaly_result = {
    "anomalies_detected": [
        {
            "record_index": 42,
            "field": "amount",
            "value": 999999.99,
            "method": "statistical",
            "reasons": ["Z-score extremo: 4.5", "Fuera de IQR"],
            "z_score": 4.5
        }
    ],
    "anomaly_count": 1,
    "scores": {
        "total_anomalies": 1,
        "unique_records_with_anomalies": 1,
        "anomaly_rate": 0.01
    }
}
```

### Auto-tuning de Rendimiento

Sistema de optimización automática:
- Análisis de métricas históricas (últimos 7 días)
- Recomendaciones para batch_size, max_workers, chunk_size
- Score de optimización (0-100)
- Tracking de throughput, tiempo, errores

```sql
-- Ver métricas de rendimiento históricas
SELECT 
    DATE(execution_date) as date,
    AVG(execution_time_seconds) as avg_time,
    AVG(throughput_records_per_sec) as avg_throughput,
    AVG(error_rate) as avg_error_rate,
    COUNT(*) as executions
FROM performance_metrics
WHERE execution_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date
ORDER BY date DESC;

-- Ver recomendaciones de optimización
SELECT 
    report_data->'performance_recommendations'->'recommendations' as recommendations,
    report_data->'performance_recommendations'->'optimization_score' as score
FROM data_integration_reports
WHERE report_data->'performance_recommendations' IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;
```

### Catálogo de Datos

Registro automático de metadatos:
- Esquemas de tablas
- Descripciones y tags
- Ownership y versionado
- Búsqueda y descubrimiento

```sql
-- Ver todas las tablas en el catálogo
SELECT 
    table_name,
    description,
    tags,
    owner,
    updated_at
FROM data_catalog
ORDER BY updated_at DESC;

-- Buscar tablas por tag
SELECT table_name, description
FROM data_catalog
WHERE tags @> '["etl"]'::jsonb;
```

### Contratos de Datos

Validación automática contra contratos:
- Reglas: not_null, unique, range, custom
- Severidad: error, warning
- Tracking de violaciones

```sql
-- Ver violaciones de contratos
SELECT 
    contract_name,
    table_name,
    rule_name,
    violations_count,
    message,
    created_at
FROM data_contract_violations
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Resumen de violaciones por contrato
SELECT 
    contract_name,
    COUNT(*) as total_violations,
    SUM(violations_count) as total_records_affected
FROM data_contract_violations
GROUP BY contract_name
ORDER BY total_violations DESC;
```

### Pruebas Automatizadas

Suite completa de pruebas end-to-end:
- **extraction_completeness**: Verifica que todas las fuentes tengan datos
- **transformation_integrity**: Valida campos requeridos
- **validation_quality**: Verifica tasa de validación
- **load_consistency**: Valida tasa de éxito de carga
- **end_to_end_flow**: Prueba retención de datos end-to-end

```sql
-- Ver resultados de pruebas recientes
SELECT 
    test_run_id,
    test_name,
    status,
    message,
    created_at
FROM pipeline_test_results
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC, test_name;

-- Resumen de pruebas por estado
SELECT 
    status,
    COUNT(*) as count,
    COUNT(DISTINCT test_run_id) as test_runs
FROM pipeline_test_results
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY status;
```

## Flujo de Procesamiento

### 1. Extracción

- **CRM**: Extrae contactos/leads modificados en el período
- **Google Sheets**: Extrae todas las filas del rango especificado
- **Facturación**: Extrae facturas y pagos del período

### 2. Transformación

- Normaliza campos comunes entre fuentes
- Mapea campos específicos de cada sistema
- Conserva datos originales en `raw_data`

### 3. Validación

- Valida formato de emails
- Valida montos y monedas
- Detecta campos requeridos faltantes
- Genera warnings y errors de validación

### 4. Carga

- Crea tabla `data_warehouse_integration` si no existe
- Inserta/actualiza registros en batches
- Maneja duplicados con `ON CONFLICT`

### 5. Detección de Inconsistencias

Detecta:
- **Emails duplicados**: Mismo email con diferentes customer_id
- **Montos inconsistentes**: Facturas para clientes marcados como "closed-lost"
- **Campos faltantes**: Registros sin customer_id
- **Errores de validación**: Registros con errores de validación

### 6. Alertas

- Envía alertas a Slack con resumen de inconsistencias
- Envía email para inconsistencias de alta severidad
- Incluye detalles y contexto de cada inconsistencia

## Esquema de la Tabla Data Warehouse

```sql
CREATE TABLE data_warehouse_integration (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(255) NOT NULL,
    source_type VARCHAR(100) NOT NULL,
    customer_id VARCHAR(255),
    email VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    amount DECIMAL(15, 2),
    currency VARCHAR(10),
    status VARCHAR(50),
    raw_data JSONB,
    validation_errors JSONB,
    validation_warnings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, source_type)
);
```

## Ejemplos de Uso

### Ejecución Manual con Parámetros

```python
# Desde Airflow UI o API
{
    "crm_type": "pipedrive",
    "crm_config": '{"api_token": "...", "company_domain": "..."}',
    "sheets_spreadsheet_id": "1abc123...",
    "enable_alerts": true,
    "dry_run": false
}
```

### Consultas Útiles

```sql
-- Ver todas las inconsistencias detectadas
SELECT 
    source_type,
    COUNT(*) as count,
    COUNT(CASE WHEN validation_errors IS NOT NULL THEN 1 END) as errors
FROM data_warehouse_integration
GROUP BY source_type;

-- Encontrar emails duplicados
SELECT 
    email,
    COUNT(DISTINCT customer_id) as customer_count,
    array_agg(DISTINCT source_type) as sources
FROM data_warehouse_integration
WHERE email IS NOT NULL
GROUP BY email
HAVING COUNT(DISTINCT customer_id) > 1;

-- Ver registros con errores de validación
SELECT 
    source_id,
    source_type,
    validation_errors
FROM data_warehouse_integration
WHERE validation_errors IS NOT NULL
AND jsonb_array_length(validation_errors) > 0;
```

## Monitoreo

### Métricas Clave

El DAG registra métricas usando Airflow Stats:

**Extracción:**
- `data_integration_etl.extract_crm_data.records` - Registros extraídos del CRM
- `data_integration_etl.extract_crm_data.count` - Total de registros
- `data_integration_etl.extract_crm_data.duration_ms` - Duración de extracción

**Transformación:**
- `data_integration_etl.transform_data.total_records` - Total de registros transformados
- `data_integration_etl.transform_data.{source}.input` - Registros de entrada por fuente
- `data_integration_etl.transform_data.{source}.output` - Registros transformados exitosamente
- `data_integration_etl.transform_data.{source}.errors` - Errores por fuente

**Validación:**
- `data_integration_etl.validate_data.total` - Total de registros validados
- `data_integration_etl.validate_data.valid` - Registros válidos
- `data_integration_etl.validate_data.invalid` - Registros inválidos
- `data_integration_etl.validate_data.errors_count` - Número de errores
- `data_integration_etl.validate_data.warnings_count` - Número de warnings

**Carga:**
- `data_integration_etl.load_to_warehouse.loaded` - Registros cargados exitosamente
- `data_integration_etl.load_to_warehouse.errors` - Errores en carga
- `data_integration_etl.load_to_warehouse.success_rate` - Tasa de éxito (%)

**Detección de Inconsistencias:**
- `data_integration_etl.detect_inconsistencies.total` - Total de inconsistencias
- `data_integration_etl.detect_inconsistencies.{severity}` - Inconsistencias por severidad

**Métricas por Etapa:**
- `data_integration_etl.{stage}.start` - Inicio de etapa
- `data_integration_etl.{stage}.success` - Éxito de etapa
- `data_integration_etl.{stage}.error` - Errores de etapa
- `data_integration_etl.{stage}.duration_ms` - Duración de etapa

### Alertas

Las alertas se envían automáticamente cuando:
- Se detectan inconsistencias de alta severidad
- Falla la extracción de alguna fuente
- Hay errores de validación significativos

### Timeouts

Cada tarea tiene timeouts configurables:
- `extract_crm_data`: 15 minutos
- `transform_data`: 30 minutos
- `validate_data`: 15 minutos
- `load_to_warehouse`: 45 minutos
- `detect_inconsistencies`: 10 minutos

### Logs

Revisar logs en:
- `extract_crm_data`: Extracción de CRM
- `extract_sheets_data`: Extracción de Google Sheets
- `extract_billing_data`: Extracción de facturación
- `transform_data`: Transformación y normalización
- `validate_data`: Validación de calidad
- `load_to_warehouse`: Carga en data warehouse
- `detect_inconsistencies`: Detección de inconsistencias
- `send_alerts`: Envío de alertas

## Troubleshooting

### Error: No se pudo conectar al CRM

1. Verificar credenciales en `crm_config`
2. Verificar que el CRM esté accesible
3. Revisar logs de conexión

### Error: No se pudo conectar a Google Sheets

1. Verificar que el spreadsheet_id sea correcto
2. Verificar credenciales de Service Account
3. Verificar que el Service Account tenga acceso al spreadsheet

### Error: Fallo en la carga

1. Verificar conexión a PostgreSQL
2. Verificar permisos de escritura
3. Revisar tamaño de batch (reducir si es necesario)

### Inconsistencias Frecuentes

1. Revisar reglas de validación
2. Verificar calidad de datos en fuentes
3. Ajustar transformaciones si es necesario

## Mejoras Futuras

- [ ] Soporte para más fuentes de datos (HubSpot, QuickBooks, etc.)
- [ ] Transformaciones más avanzadas con dbt
- [ ] Detección de anomalías con ML
- [ ] Dashboard de métricas en tiempo real
- [ ] Resolución automática de inconsistencias
- [ ] Sincronización bidireccional

## Soporte

Para problemas o preguntas, contactar al equipo de Data Engineering.

