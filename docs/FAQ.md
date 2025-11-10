# ❓ Preguntas Frecuentes (FAQ)

> **Versión**: 1.0 | **Última actualización**: 2024

Preguntas frecuentes y respuestas sobre la plataforma.

## 📋 Tabla de Contenidos

- [General](#-general)
- [Airflow](#-airflow)
- [Kubernetes](#-kubernetes)
- [Base de Datos](#-base-de-datos)
- [Sistema de Aprobaciones](#-sistema-de-aprobaciones)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)

---

## 🌐 General

### ¿Qué es esta plataforma?

Es una plataforma de automatización empresarial que integra:
- **Orquestación**: Airflow, Kestra, Flowable, Camunda
- **ETL**: Pipelines de datos
- **MLOps**: MLflow, KServe, Kubeflow
- **Observabilidad**: Prometheus, Grafana, Loki
- **Seguridad**: Vault, OPA, External Secrets

### ¿Cómo empiezo?

1. Lee el [Quick Start Guide](./QUICK_START.md) (15 minutos)
2. Revisa los [Ejemplos Prácticos](./EJEMPLOS_PRACTICOS.md)
3. Consulta la [Guía de Desarrollo](./DESARROLLO.md)

### ¿Qué documentación debo leer primero?

**Por rol**:
- **Desarrollador**: [DESARROLLO.md](./DESARROLLO.md) → [EJEMPLOS_PRACTICOS.md](./EJEMPLOS_PRACTICOS.md)
- **DevOps**: [DEPLOYMENT.md](./DEPLOYMENT.md) → [OPERACION.md](./OPERACION.md)
- **Arquitecto**: [ARQUITECTURA.md](./ARQUITECTURA.md) → [DIAGRAMAS.md](./DIAGRAMAS.md)

**Para empezar rápido**: [QUICK_START.md](./QUICK_START.md)

---

## ✈️ Airflow

### ¿Cómo creo mi primer DAG?

Ver [QUICK_START.md](./QUICK_START.md) o [EJEMPLOS_PRACTICOS.md](./EJEMPLOS_PRACTICOS.md) para ejemplos.

### ¿Por qué mi DAG no aparece en la UI?

**Causas comunes**:
1. Errores de importación
2. Archivo no está en el directorio correcto
3. Scheduler no está corriendo

**Solución**:
```bash
# Verificar errores
airflow dags list-import-errors

# Verificar ubicación
ls -la data/airflow/dags/

# Reiniciar scheduler
docker-compose restart airflow-scheduler
```

### ¿Cómo manejo errores en tareas?

Usa retry logic y callbacks:
```python
@task(
    retries=3,
    retry_delay=timedelta(minutes=5),
    on_failure_callback=on_task_failure
)
def mi_tarea():
    # Tu código
    pass
```

Ver [BEST_PRACTICES.md](./BEST_PRACTICES.md) para más detalles.

### ¿Cómo paso parámetros a un DAG?

```python
@dag(
    params={
        "batch_size": Param(1000, type="integer"),
    }
)
def mi_dag():
    @task
    def procesar(**context):
        batch_size = context["params"]["batch_size"]
        # Usar batch_size
```

O desde CLI:
```bash
airflow dags trigger mi_dag --conf '{"batch_size": 2000}'
```

### ¿Cómo uso plugins modulares?

```python
from data.airflow.plugins.approval_cleanup_config import get_config
from data.airflow.plugins.approval_cleanup_ops import get_pg_hook

config = get_config()
pg_hook = get_pg_hook()
```

Ver [APPROVAL_SYSTEM.md](./APPROVAL_SYSTEM.md) para más detalles.

---

## ☸️ Kubernetes

### ¿Cómo accedo a un pod para debugging?

```bash
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash
```

### ¿Cómo veo logs de un pod?

```bash
# Logs simples
kubectl logs <pod-name> -n <namespace>

# Logs con seguimiento
kubectl logs -f <pod-name> -n <namespace>

# Logs de múltiples pods
kubectl logs -f -l app=<app-name> -n <namespace>
```

### ¿Cómo escalo un deployment?

```bash
kubectl scale deployment <deployment-name> --replicas=5 -n <namespace>
```

### ¿Cómo hago port-forward?

```bash
kubectl port-forward -n <namespace> service/<service-name> <local-port>:<service-port>

# Ejemplo: Grafana
kubectl port-forward -n observability service/prometheus-grafana 3000:80
```

### ¿Cómo veo qué está pasando en el cluster?

```bash
# Ver todos los recursos
kubectl get all -n <namespace>

# Ver eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Ver recursos de pods
kubectl top pods -n <namespace>
```

---

## 🗄️ Base de Datos

### ¿Cómo me conecto a PostgreSQL?

```bash
psql -h <host> -U <user> -d <database>
```

O desde Python:
```python
from airflow.providers.postgres.hooks.postgres import PostgresHook

hook = PostgresHook(postgres_conn_id="postgres_default")
result = hook.get_records("SELECT * FROM tabla")
```

### ¿Cómo hago backup de la base de datos?

```bash
pg_dump -h <host> -U <user> -d <database> > backup.sql
```

### ¿Cómo veo queries lentas?

```sql
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### ¿Cómo optimizo índices?

```sql
-- Analizar tabla
ANALYZE tabla;

-- Reindexar
REINDEX TABLE tabla;

-- Ver índices no usados
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

---

## ✅ Sistema de Aprobaciones

### ¿Por qué el DAG approval_cleanup.py es tan grande?

El archivo tiene **32,609 líneas** porque contiene toda la funcionalidad en un solo archivo. 

**Recomendación**: Usar la versión simplificada con plugins modulares que reduce el código en **97%**.

Ver [APPROVAL_SYSTEM_MEJORAS.md](./APPROVAL_SYSTEM_MEJORAS.md) para más detalles.

### ¿Cómo migro a la versión simplificada?

Ver [GUIA_MIGRACION.md](./GUIA_MIGRACION.md) para guía paso a paso.

### ¿Qué plugins están disponibles?

Ver [APPROVAL_SYSTEM.md](./APPROVAL_SYSTEM.md) para lista completa de plugins.

### ¿Cómo configuro las variables de entorno?

Usa `approval_cleanup_config.py` para configuración centralizada:

```python
from data.airflow.plugins.approval_cleanup_config import get_config

config = get_config()
retention_years = config['retention']['years']
```

---

## ⚡ Performance

### ¿Cómo mejoro la performance de mis DAGs?

1. **Procesamiento en lotes**: Usar batch processing
2. **Connection pooling**: Reutilizar conexiones
3. **Caching**: Cachear resultados costosos
4. **Parallel processing**: Usar task groups paralelos

Ver [BEST_PRACTICES.md](./BEST_PRACTICES.md) para más detalles.

### ¿Cómo identifico cuellos de botella?

```bash
# Ver queries lentas en PostgreSQL
# Ver métricas en Prometheus
# Ver logs de performance
```

### ¿Cómo optimizo queries SQL?

1. Crear índices apropiados
2. Usar EXPLAIN ANALYZE
3. Evitar N+1 queries
4. Usar batch processing

---

## 🔍 Troubleshooting

### El DAG tarda mucho en cargar

**Causa**: Archivo muy grande (32,609 líneas)

**Solución**:
1. Usar plugins modulares
2. Dividir DAG en múltiples DAGs
3. Eliminar imports no usados

Ver [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) para más soluciones.

### Error "Module not found"

**Solución**:
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project"

# Verificar imports
python -c "from data.airflow.plugins.approval_cleanup_config import get_config; print('OK')"
```

### Error de conexión a base de datos

**Solución**:
```bash
# Verificar connection ID
airflow connections list | grep <connection-id>

# Probar conexión
python -c "from airflow.providers.postgres.hooks.postgres import PostgresHook; h = PostgresHook(postgres_conn_id='<id>'); print(h.get_conn())"
```

### Pods en CrashLoopBackOff

**Solución**:
1. Ver logs: `kubectl logs <pod-name> -n <namespace>`
2. Verificar configuración (secrets, configmaps)
3. Verificar recursos (CPU/memoria)
4. Verificar health checks

### Tarea falla repetidamente

**Solución**:
1. Aumentar timeout
2. Aumentar recursos del worker
3. Verificar dependencias externas
4. Revisar código para errores

Ver [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) para más soluciones.

---

## 📚 Referencias

- [`docs/QUICK_START.md`](./QUICK_START.md) - Guía rápida
- [`docs/TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) - Troubleshooting completo
- [`docs/REFERENCIA_RAPIDA.md`](./REFERENCIA_RAPIDA.md) - Referencia rápida
- [`docs/BEST_PRACTICES.md`](./BEST_PRACTICES.md) - Mejores prácticas

---

**Versión**: 1.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

