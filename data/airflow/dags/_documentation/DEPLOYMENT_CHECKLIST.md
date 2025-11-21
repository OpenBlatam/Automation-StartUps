# Checklist de Deployment - ETL Mejorado

Lista de verificación para desplegar el sistema ETL mejorado en producción.

## Pre-Deployment

### ✅ Base de Datos

- [ ] PostgreSQL >= 12 instalado y accesible
- [ ] Connection string `KPIS_PG_DSN` configurado y probado
- [ ] Backup de base de datos existente realizado (si hay datos)
- [ ] Scripts de backup/restore probados (`data/db/etl_backup.sh`, `data/db/etl_restore.sh`)
- [ ] Ejecutar `data/db/etl_setup.sql` para setup inicial
- [ ] Si hay instalación existente, ejecutar `data/db/etl_migration.sql`
- [ ] Verificar que todas las tablas se crearon correctamente:
  ```sql
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name LIKE 'etl_improved%';
  ```
- [ ] Verificar índices:
  ```sql
  SELECT indexname FROM pg_indexes 
  WHERE schemaname = 'public' 
  AND tablename LIKE 'etl_improved%';
  ```
- [ ] Verificar materialized views:
  ```sql
  SELECT matviewname FROM pg_matviews 
  WHERE schemaname = 'public' 
  AND matviewname LIKE 'mv_etl%';
  ```

### ✅ Variables de Entorno Airflow

- [ ] `KPIS_PG_DSN`: Connection string PostgreSQL configurado
- [ ] `SLACK_WEBHOOK`: URL webhook de Slack (opcional, para alertas)
- [ ] `SLACK_CONN_ID`: ID de conexión Airflow para Slack provider (opcional)
- [ ] `MLFLOW_TRACKING_URI`: URI del servidor MLflow (opcional)
- [ ] `ETL_POOL`: Pool de Airflow para limitar concurrencia (opcional)

### ✅ Airflow Variables (Opcional - para defaults)

- [ ] `etl_improved__batch_size`: Tamaño de batch por defecto
- [ ] `etl_improved__chunk_size`: Tamaño de chunk por defecto
- [ ] `etl_improved__run_label`: Etiqueta por defecto
- [ ] `etl_improved__schema_name`: Schema por defecto
- [ ] `etl_improved__table_name`: Tabla por defecto
- [ ] `etl_improved__enforce_ge`: Forzar Great Expectations (si aplica)
- [ ] `etl_improved__mlflow_enable`: Habilitar MLflow (si aplica)

### ✅ Conexiones Airflow

- [ ] Slack connection configurada (si se usa provider nativo):
  ```bash
  airflow connections add slack_default \
    --conn-type http \
    --conn-host https://hooks.slack.com \
    --conn-password <webhook_url>
  ```

### ✅ Dependencias Python

- [ ] `psycopg` o `psycopg2` instalado
- [ ] `polars` instalado (opcional, para transformación rápida)
- [ ] `pydantic` instalado (opcional, para validación)
- [ ] `great_expectations` instalado (opcional, si `enforce_ge=True`)
- [ ] `mlflow` instalado (opcional, si `mlflow_enable=True`)
- [ ] `airflow.providers.slack` instalado (opcional, para notificaciones nativas)

### ✅ DAGs

- [ ] `etl_improved.py` cargado en Airflow
- [ ] `etl_consumer.py` cargado en Airflow
- [ ] `etl_maintenance.py` cargado en Airflow
- [ ] `etl_downstream_example.py` cargado (si se usa como plantilla)
- [ ] Verificar que DAGs aparecen en la UI sin errores
- [ ] Verificar que no hay errores de sintaxis:
  ```bash
  airflow dags list | grep etl
  ```

## Deployment

### ✅ Primera Ejecución

- [ ] Ejecutar `etl_improved` en modo dry-run:
  ```bash
  airflow dags trigger etl_improved \
    --conf '{"dry_run": true, "batch_size": 10}'
  ```
- [ ] Verificar que todas las tareas completan exitosamente
- [ ] Verificar logs para asegurar que no hay errores
- [ ] Ejecutar ejecución real con batch pequeño:
  ```bash
  airflow dags trigger etl_improved \
    --conf '{"batch_size": 100, "run_label": "deployment_test"}'
  ```
- [ ] Verificar que datos se insertan correctamente:
  ```sql
  SELECT COUNT(*) FROM public.etl_improved_metrics;
  SELECT * FROM public.etl_improved_metrics ORDER BY at DESC LIMIT 5;
  ```
- [ ] Verificar que `etl_consumer` se ejecuta automáticamente (triggered por Dataset)
- [ ] Verificar que materialized views se refrescan:
  ```sql
  SELECT * FROM public.mv_etl_metrics_daily ORDER BY day DESC LIMIT 5;
  ```

### ✅ Configuración de Schedule

- [ ] `etl_improved`: Schedule `@daily` activado
- [ ] `etl_maintenance`: Schedule `@weekly` activado
- [ ] Verificar timezones y horarios apropiados

## Post-Deployment

### ✅ Dashboard Next.js

- [ ] Aplicación Next.js desplegada y accesible
- [ ] Variables de entorno de BD configuradas
- [ ] Dashboard `/etl` accesible y mostrando datos
- [ ] Healthcheck `/api/etl/health` funcionando:
  ```bash
  curl http://your-app/api/etl/health
  ```
- [ ] Métricas Prometheus `/api/etl/metrics` exportando:
  ```bash
  curl http://your-app/api/etl/metrics
  ```

### ✅ Observabilidad

- [ ] ServiceMonitor `etl-metrics.yaml` aplicado (si usa Prometheus Operator)
- [ ] Prometheus scrapeando métricas del ETL
- [ ] Dashboard Grafana `etl_improved.json` importado
- [ ] Verificar que métricas aparecen en Grafana
- [ ] Verificar que materialized views se refrescan automáticamente

### ✅ Alertas

- [ ] Slack webhook configurado y probado
- [ ] Ejecutar DAG con ratio < 1.0 para probar alertas
- [ ] Verificar que alertas se envían a Slack
- [ ] Verificar que alertas se persisten en `etl_improved_alerts`

### ✅ Mantenimiento

- [ ] `etl_maintenance` ejecutado manualmente al menos una vez
- [ ] Verificar que limpia datos antiguos correctamente
- [ ] Verificar que VACUUM ANALYZE funciona
- [ ] Verificar que no hay errores en logs

### ✅ Tests

- [ ] Ejecutar tests de estructura:
  ```bash
  cd data/airflow
  python -m pytest tests/test_etl_dags.py -v
  ```
- [ ] Todos los tests pasan

## Monitoreo Continuo

### ✅ Verificaciones Regulares

- [ ] Monitorear logs de `etl_improved` diariamente
- [ ] Revisar métricas en dashboard `/etl` semanalmente
- [ ] Verificar ratios en Grafana
- [ ] Revisar alertas generadas
- [ ] Verificar que `etl_maintenance` se ejecuta semanalmente
- [ ] Revisar tamaño de tablas y considerar ajustar retención si es necesario

### ✅ Performance

- [ ] Monitorear duración de tareas en Airflow UI
- [ ] Verificar que `load` task no excede SLA (15 min)
- [ ] Ajustar `chunk_size` si hay problemas de performance
- [ ] Monitorear uso de recursos (CPU, memoria, conexiones DB)

## Rollback Plan

### ✅ En Caso de Problemas

- [ ] Desactivar DAGs inmediatamente en Airflow UI
- [ ] Revisar logs para identificar problema
- [ ] Si hay datos corruptos, restaurar desde backup
- [ ] Revisar `etl_improved_alerts` para identificar problemas
- [ ] Corregir problemas y reactivar DAGs
- [ ] Ejecutar en dry-run primero para validar

## Documentación

- [ ] Equipo familiarizado con `README_ETL_IMPROVED.md`
- [ ] Índice `INDEX_ETL_IMPROVED.md` disponible para referencia
- [ ] Runbooks documentados para troubleshooting común

---

**Última actualización**: Verificar este checklist antes de cada deployment importante.

