# Airflow - Operación y Configuración

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Guía completa para operar y configurar Airflow en la plataforma de automatización empresarial.

## 📋 Tabla de Contenidos

- [Variables y Configuración](#variables-y-configuración)
- [Notificaciones](#notificaciones)
- [Pools y Recursos](#pools-y-recursos)
- [DAGs Principales](#dags-principales)
- [Desarrollo Local](#desarrollo-local)
- [Operación](#operación)
- [Troubleshooting](#troubleshooting)
- [Referencias](#referencias)

## Variables y Configuración

### Variables de Entorno Críticas

Estas variables se inyectan vía Helm en `values.yaml` (`workers.env`). Los secretos se montan con External Secret `airflow-secrets` (ver `security/secrets/externalsecrets-airflow-notify.yaml`).

#### Notificaciones

**Slack**
- `ENABLE_SLACK`: `"true"` / `"false"` (default: `true`)
- `SLACK_WEBHOOK_URL`: Webhook entrante de Slack

**Email**
- `ENABLE_EMAIL`: `"true"` / `"false"` (default: `false`)
- `ALERT_EMAILS`: Lista de emails separada por comas (ej: `"ops@example.com, data@example.com"`)

**Sentry** (Opcional)
- `ENABLE_SENTRY`: `"true"` / `"false"` (default: `false`)
- `SENTRY_DSN`: DSN del proyecto Sentry

**OpenTelemetry** (Opcional)
- `ENABLE_OTEL`: `"true"` / `"false"` (default: `false`)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: Endpoint del collector (ej: `http://otel-collector:4318`)
- `OTEL_SERVICE_NAME`: Nombre del servicio (ej: `airflow-etl`)

#### Operación ETL

- `ETL_POOL`: Nombre del pool usado por tareas ETL (default: `etl_pool`)
- `MAX_ACTIVE_TASKS`: Límite de tareas activas del DAG (default: `32`)
- `CHUNK_PARALLELISM`: Límite de TaskInstances activas por tarea mapeada (default: `16`)

#### Integraciones Externas

**Stripe + QuickBooks**
- `STRIPE_API_KEY`: API key de Stripe para obtener pagos y tarifas
- `QUICKBOOKS_ACCESS_TOKEN`: Access token OAuth2 de QuickBooks Online
- `QUICKBOOKS_REALM_ID`: Company ID (Realm ID) de QuickBooks

**Configuración**: Los secretos se sincronizan desde AWS Secrets Manager vía External Secrets (`security/secrets/externalsecrets-stripe-quickbooks.yaml`).

**DAGs relacionados**: `stripe_fees_to_quickbooks` - Crea gastos en QuickBooks para tarifas de Stripe automáticamente.

Ver [`dags/INDEX_FINANCIAL.md`](./dags/INDEX_FINANCIAL.md) para documentación completa de DAGs financieros.

### Configuración por Entorno

La configuración puede variar por entorno (dev/stg/prod). Ver `environments/*.yaml` para valores específicos por entorno.

## Notificaciones

### Slack

Las notificaciones a Slack se envían automáticamente cuando:
- Un DAG falla
- Se produce un SLA miss
- Un task falla después de todos los retries

**Configurar**:
```bash
# En values.yaml o via External Secrets
ENABLE_SLACK=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Formato de mensajes**:
- Incluyen contexto completo: DAG ID, task ID, run ID, timestamp
- Enlaces a logs y UI de Airflow
- Información de error detallada

### Email

Las notificaciones por email se envían a las direcciones configuradas en `ALERT_EMAILS`.

**Configurar**:
```bash
ENABLE_EMAIL=true
ALERT_EMAILS="ops@example.com,data@example.com"
```

### Sentry (Opcional)

Integración con Sentry para tracking de errores y excepciones.

**Configurar**:
```bash
ENABLE_SENTRY=true
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Pools y Recursos

### Pool de ETL

El pool `etl_pool` controla la concurrencia de tareas ETL:

**Configuración**:
- **Ubicación**: Airflow UI → Admin → Pools
- **Slots**: Configurable según capacidad de workers (default: 32)
- **Ajuste**: Aumentar slots para más paralelismo, reducir para limitar recursos

**Uso en DAGs**:
```python
@task(pool="etl_pool")
def extract():
    # Task que usa el pool
    pass
```

### Otros Pools

- `dq_pool`: Para tareas de data quality (16 slots)
- `onboarding_pool`: Para procesos de onboarding (8 slots)

### Gestión de Recursos

- **Resource Quotas**: `security/kubernetes/limitranges-quotas.yaml`
- **Pod Limits**: Configurados en `values.yaml` para workers
- **Horizontal Pod Autoscaler**: Para auto-escalado según carga

## DAGs Principales

### `etl_example` ⭐

Pipeline ETL completo con validaciones robustas.

**Trigger**: Por Dataset (`dataset://source_ready`)

**Parámetros** (con schema validation):
```json
{
  "rows": 500000,           // int, 1..10e6
  "run_name": "ad_hoc_run", // string
  "since": "2024-01-01T00:00:00Z",  // ISO8601
  "until": "2024-01-31T23:59:59Z",  // ISO8601
  "chunk_rows": 100000,     // int, opcional
  "min_rows": 1000,          // int, DQ threshold
  "max_rows": 10000000,      // int, DQ threshold
  "allow_overwrite": false,  // bool, bypass idempotency
  "dry_run": false          // bool, skip side-effects
}
```

**Características**:
- ✅ Idempotencia avanzada con TTL y checksums
- ✅ Circuit breaker automático
- ✅ Validación robusta de schemas
- ✅ Data Quality checks configurables
- ✅ Detección de anomalías
- ✅ Health checks pre-vuelo
- ✅ Lineage completo con datasets
- ✅ Métricas avanzadas (throughput, duración)

**Documentación completa**: [`dags/INDEX_ETL_IMPROVED.md`](./dags/INDEX_ETL_IMPROVED.md)

### Otros DAGs Importantes

- **`employee_onboarding`**: Automatización completa de onboarding
- **`kpi_reports_monthly`**: Reportes mensuales de KPIs
- **`stripe_reconcile`**: Reconciliación de pagos Stripe
- **`stripe_fees_to_quickbooks`**: Crea gastos en QuickBooks para tarifas de Stripe
- **`outreach_multichannel`**: Automatización multi-canal de outreach
- **`etl_maintenance`**: Limpieza y mantenimiento automatizado

**DAGs Financieros**: Ver [`dags/INDEX_FINANCIAL.md`](./dags/INDEX_FINANCIAL.md) para documentación completa de todos los DAGs financieros.

**Ver todos**: [`dags/INDEX_ETL_IMPROVED.md`](./dags/INDEX_ETL_IMPROVED.md)

## Desarrollo Local

### Configuración Rápida

```bash
# Variables de entorno para desarrollo local
export ENABLE_SLACK=true
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export ENABLE_EMAIL=false
export ALERT_EMAILS="ops@example.com, data@example.com"
export ENABLE_SENTRY=false
export SENTRY_DSN=""
export ENABLE_OTEL=false
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
export OTEL_SERVICE_NAME="airflow-etl"
export ETL_POOL=etl_pool
export MAX_ACTIVE_TASKS=32
export CHUNK_PARALLELISM=16
```

### Docker Compose

Usar `docker-compose.yml` para levantar Airflow localmente:

```bash
# Levantar Airflow
make airflow-up
# O directamente:
docker-compose up -d

# Inicializar base de datos (primera vez)
make airflow-init
# O directamente:
docker-compose run airflow-webserver airflow db init
docker-compose run airflow-webserver airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname User \
  --role Admin --email admin@example.com

# Acceder a UI
# http://localhost:8080 (admin/admin)
```

### Testing Local

```bash
# Test de un DAG completo
airflow dags test etl_example

# Test de una tarea específica
airflow tasks test etl_example extract 2024-01-01

# Listar DAGs
airflow dags list

# Verificar errores de importación
airflow dags list-import-errors
```

### Desarrollar Nuevos DAGs

1. **Crear archivo**: `data/airflow/dags/mi_dag.py`
2. **Usar patrones**: Ver [`dags/INDEX_ETL_IMPROVED.md`](./dags/INDEX_ETL_IMPROVED.md) - Sección "Patrones de Diseño"
3. **Importar utilidades**: 
   ```python
   from etl_config_constants import *
   from etl_utils import calculate_throughput, log_task_metrics
   ```
4. **Testing**: Crear tests en `tests/` siguiendo ejemplos en `tests/test_etl_dags.py`

## Operación

### Comandos Útiles

```bash
# Listar DAGs
airflow dags list

# Ver estado de un DAG
airflow dags show etl_example

# Trigger manual de un DAG
airflow dags trigger etl_example \
  --conf '{"rows": 10000, "run_name": "manual_run"}'

# Ver logs de una ejecución
airflow tasks logs etl_example extract 2024-01-01

# Pausar/despausar DAG
airflow dags pause etl_example
airflow dags unpause etl_example

# Ver variables
airflow variables list
airflow variables get ENABLE_SLACK

# Ver conexiones
airflow connections list
```

### Monitoreo

**UI de Airflow**:
- Acceso: `http://airflow.your-domain.com`
- Dashboards: Ver DAGs, tareas, ejecuciones
- Logs: Acceso directo a logs de tareas
- Métricas: StatsD integrado

**Grafana**:
- Dashboards: `observability/grafana/dashboards/`
- Métricas de Airflow exportadas automáticamente
- Ver [`observability/README.md`](../../observability/README.md)

**Prometheus**:
- ServiceMonitor: `observability/servicemonitors/airflow.yaml`
- Métricas: `/metrics` endpoint expuesto por Airflow

### Gestión de Pools

```bash
# Ver pools
airflow pools list

# Editar pool (vía UI o CLI)
# UI: Admin → Pools
```

### Variables y Conexiones

```bash
# Listar variables
airflow variables list

# Obtener variable
airflow variables get ENABLE_SLACK

# Setear variable
airflow variables set ENABLE_SLACK true

# Listar conexiones
airflow connections list

# Obtener conexión
airflow connections get postgres_default
```

## Troubleshooting

### DAGs no se ejecutan

```bash
# Verificar errores de importación
airflow dags list-import-errors

# Verificar variables y conexiones
airflow variables list
airflow connections list

# Verificar estado de scheduler
kubectl logs -n airflow deployment/airflow-scheduler

# Verificar pools
airflow pools list
```

### Tareas fallan

1. **Revisar logs**:
   ```bash
   airflow tasks logs etl_example extract 2024-01-01
   ```

2. **Verificar dependencias**:
   - Variables de entorno configuradas
   - Conexiones válidas
   - Pools con slots disponibles

3. **Revisar circuit breaker**:
   ```bash
   airflow variables get cb:failures:etl_example
   ```

4. **Verificar rate limits**:
   ```bash
   airflow variables get rate_limit:mlflow_api
   ```

### Performance lento

1. **Revisar métricas de throughput**:
   - En logs: buscar `throughput_rows_per_sec`
   - En Grafana: dashboard de ETL

2. **Ajustar paralelismo**:
   - Aumentar `CHUNK_PARALLELISM`
   - Aumentar slots en `etl_pool`
   - Revisar límites de workers

3. **Revisar chunking**:
   - Ajustar `chunk_rows` en parámetros del DAG
   - Ver [`dags/INDEX_ETL_IMPROVED.md`](./dags/INDEX_ETL_IMPROVED.md) - Sección "Performance Tuning"

### Circuit Breaker Abierto

```bash
# Ver estado
airflow variables get cb:failures:etl_example

# Resetear manualmente
airflow variables delete cb:failures:etl_example

# Ver logs de fallos previos
kubectl logs -n airflow deployment/airflow-worker | grep "circuit_breaker"
```

### Rate Limit Excedido

```bash
# Ver estado actual
airflow variables get rate_limit:mlflow_api | jq

# Resetear manualmente (si es necesario)
airflow variables delete rate_limit:mlflow_api
```

## Referencias

### Documentación Completa

- **Índice ETL**: [`dags/INDEX_ETL_IMPROVED.md`](./dags/INDEX_ETL_IMPROVED.md) ⭐
- **Mejoras**: [`dags/ETL_IMPROVEMENTS.md`](./dags/ETL_IMPROVEMENTS.md)
- **Onboarding**: [`README_onboarding.md`](./README_onboarding.md)

### Archivos Clave

- **Constantes**: `dags/etl_config_constants.py`
- **Utilidades**: `dags/etl_utils.py`
- **Plugins**: `plugins/`
- **Tests**: `tests/`

### Enlaces Externos

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: Data Engineering Team  
**Última actualización**: 2024
