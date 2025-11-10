# 🔍 Guía de Troubleshooting

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Guía completa para resolver problemas comunes en la plataforma.

## 📋 Tabla de Contenidos

- [Problemas Comunes](#-problemas-comunes)
- [Airflow](#-airflow)
- [Kubernetes](#-kubernetes)
- [Base de Datos](#-base-de-datos)
- [Integraciones](#-integraciones)
- [Performance](#-performance)
- [Comandos Útiles](#-comandos-útiles)
- [Escalación](#-escalación)

---

## 🚨 Problemas Comunes

### DAG no aparece en Airflow UI

**Síntomas**:
- DAG no visible en la lista de DAGs
- Import errors en Airflow

**Diagnóstico**:
```bash
# Verificar import errors
airflow dags list-import-errors

# Verificar logs de scheduler
kubectl logs -n airflow <scheduler-pod> | grep ERROR
```

**Soluciones**:
1. Verificar sintaxis del DAG
2. Verificar imports
3. Verificar que el DAG está en el directorio correcto
4. Reiniciar scheduler si es necesario

### Pods en CrashLoopBackOff

**Síntomas**:
- Pods reiniciándose continuamente
- Estado `CrashLoopBackOff` en Kubernetes

**Diagnóstico**:
```bash
# Ver logs del pod
kubectl logs <pod-name> -n <namespace>

# Ver eventos
kubectl describe pod <pod-name> -n <namespace>

# Verificar recursos
kubectl top pod <pod-name> -n <namespace>
```

**Soluciones comunes**:
1. **Error de configuración**: Verificar secrets/configmaps
2. **Error de conexión**: Verificar conexiones a BD/servicios
3. **Recursos insuficientes**: Aumentar requests/limits
4. **Error en código**: Verificar logs para errores

### Conexión a base de datos falla

**Síntomas**:
- Error "connection refused" o "timeout"
- Tareas fallando con error de BD

**Diagnóstico**:
```bash
# Verificar que el servicio está corriendo
kubectl get svc -n <namespace> | grep postgres

# Probar conexión desde pod
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- psql -h <host> -U <user> -d <database>

# Verificar connection ID en Airflow
airflow connections list | grep <connection-id>
```

**Soluciones**:
1. Verificar que el servicio de BD está corriendo
2. Verificar credenciales en secrets
3. Verificar network policies
4. Verificar firewall rules

---

## ✈️ Airflow

### DAG no se ejecuta

**Diagnóstico**:
```bash
# Verificar estado del DAG
airflow dags list | grep <dag-id>

# Verificar schedule
airflow dags show <dag-id>

# Verificar última ejecución
airflow dags state <dag-id> <execution-date>
```

**Soluciones**:
1. Verificar `start_date` y `schedule_interval`
2. Verificar `catchup=False` si no quieres ejecuciones pasadas
3. Verificar que el DAG está habilitado
4. Verificar que el scheduler está corriendo

### Tarea falla repetidamente

**Diagnóstico**:
```bash
# Ver logs de la tarea
airflow tasks logs <dag-id> <task-id> <execution-date>

# Ver intentos de retry
airflow tasks state <dag-id> <task-id> <execution-date>
```

**Soluciones**:
1. **Timeout**: Aumentar `execution_timeout`
2. **Recursos**: Aumentar recursos del worker
3. **Dependencias**: Verificar dependencias externas
4. **Código**: Revisar código para errores

### Workers no procesan tareas

**Diagnóstico**:
```bash
# Verificar workers
kubectl get pods -n airflow | grep worker

# Ver logs de workers
kubectl logs -n airflow <worker-pod> | grep ERROR

# Verificar queue
airflow dags list-runs -d <dag-id>
```

**Soluciones**:
1. Verificar que workers están corriendo
2. Verificar conexión a broker (Redis/RabbitMQ)
3. Verificar recursos de workers
4. Reiniciar workers si es necesario

---

## ☸️ Kubernetes

### Pods no se crean

**Diagnóstico**:
```bash
# Ver eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Verificar recursos disponibles
kubectl describe nodes

# Verificar quotas
kubectl describe quota -n <namespace>
```

**Soluciones**:
1. **Recursos insuficientes**: Liberar recursos o escalar cluster
2. **Quotas**: Verificar resource quotas
3. **Image pull errors**: Verificar acceso a registry
4. **PVC errors**: Verificar storage class

### Servicios no son accesibles

**Diagnóstico**:
```bash
# Verificar servicio
kubectl get svc -n <namespace>

# Verificar endpoints
kubectl get endpoints -n <namespace>

# Probar desde pod
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://<service-name>:<port>
```

**Soluciones**:
1. Verificar que el servicio apunta a pods correctos
2. Verificar selectors en el servicio
3. Verificar network policies
4. Verificar que los pods están running

### Ingress no funciona

**Diagnóstico**:
```bash
# Verificar ingress
kubectl get ingress -n <namespace>

# Verificar ingress controller
kubectl get pods -n ingress-nginx

# Ver logs del controller
kubectl logs -n ingress-nginx <controller-pod>
```

**Soluciones**:
1. Verificar que el ingress controller está corriendo
2. Verificar configuración del ingress
3. Verificar certificados TLS
4. Verificar DNS

---

## 🗄️ Base de Datos

### Queries lentas

**Diagnóstico**:
```sql
-- Ver queries lentas
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Ver locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Ver conexiones activas
SELECT count(*) FROM pg_stat_activity;
```

**Soluciones**:
1. **Crear índices**: Analizar queries y crear índices apropiados
2. **Optimizar queries**: Revisar y optimizar queries lentas
3. **Vacuum**: Ejecutar VACUUM ANALYZE
4. **Escalar**: Aumentar recursos de la BD si es necesario

### Conexiones agotadas

**Diagnóstico**:
```sql
-- Ver conexiones
SELECT count(*) FROM pg_stat_activity;

-- Ver límite
SHOW max_connections;

-- Ver conexiones por aplicación
SELECT application_name, count(*) 
FROM pg_stat_activity 
GROUP BY application_name;
```

**Soluciones**:
1. **Aumentar max_connections**: Si es posible
2. **Connection pooling**: Usar pgbouncer o similar
3. **Cerrar conexiones**: Asegurar que las conexiones se cierran
4. **Optimizar aplicaciones**: Reducir número de conexiones

### Bloqueos (Deadlocks)

**Diagnóstico**:
```sql
-- Ver locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Ver deadlocks en logs
-- Buscar "deadlock detected" en logs de PostgreSQL
```

**Soluciones**:
1. **Identificar queries**: Identificar queries que causan deadlocks
2. **Optimizar transacciones**: Reducir tiempo de transacciones
3. **Ordenar locks**: Asegurar orden consistente de locks
4. **Retry logic**: Implementar retry en caso de deadlock

---

## 🔗 Integraciones

### Webhook no funciona

**Diagnóstico**:
```bash
# Probar webhook manualmente
curl -X POST <webhook-url> \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Ver logs de la aplicación
kubectl logs -n <namespace> <pod-name> | grep webhook
```

**Soluciones**:
1. Verificar URL del webhook
2. Verificar autenticación
3. Verificar formato de datos
4. Verificar que el servicio está accesible

### API externa no responde

**Diagnóstico**:
```bash
# Probar API
curl -v <api-url>

# Verificar desde pod
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl <api-url>

# Ver logs
kubectl logs -n <namespace> <pod-name> | grep api
```

**Soluciones**:
1. **Verificar conectividad**: Asegurar que el servicio es accesible
2. **Verificar autenticación**: Verificar API keys/tokens
3. **Rate limiting**: Verificar si hay rate limiting
4. **Circuit breaker**: Implementar circuit breaker

---

## ⚡ Performance

### Aplicación lenta

**Diagnóstico**:
```bash
# Verificar recursos
kubectl top pods -n <namespace>

# Verificar métricas
# Acceder a Grafana y revisar dashboards

# Verificar logs de performance
kubectl logs -n <namespace> <pod-name> | grep -i "slow\|timeout"
```

**Soluciones**:
1. **Escalar horizontalmente**: Aumentar número de pods
2. **Escalar verticalmente**: Aumentar recursos
3. **Optimizar código**: Revisar y optimizar código lento
4. **Caching**: Implementar cache donde sea apropiado

### Base de datos lenta

**Diagnóstico**:
```sql
-- Ver queries activas
SELECT pid, state, query, query_start
FROM pg_stat_activity
WHERE state != 'idle';

-- Ver estadísticas de índices
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

**Soluciones**:
1. **Crear índices**: Crear índices para queries frecuentes
2. **Vacuum**: Ejecutar VACUUM ANALYZE regularmente
3. **Optimizar queries**: Revisar y optimizar queries
4. **Escalar BD**: Aumentar recursos si es necesario

---

## 🛠️ Comandos Útiles

### Kubernetes

```bash
# Ver todos los recursos
kubectl get all -n <namespace>

# Ver logs de múltiples pods
kubectl logs -f -l app=<app-name> -n <namespace>

# Ejecutar shell en pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Port-forward
kubectl port-forward -n <namespace> service/<service-name> <local-port>:<service-port>

# Ver eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Describir recurso
kubectl describe <resource-type> <resource-name> -n <namespace>
```

### Airflow

```bash
# Listar DAGs
airflow dags list

# Ver estado de DAG
airflow dags state <dag-id> <execution-date>

# Ver logs de tarea
airflow tasks logs <dag-id> <task-id> <execution-date>

# Trigger DAG
airflow dags trigger <dag-id>

# Test task
airflow tasks test <dag-id> <task-id> <execution-date>

# Ver conexiones
airflow connections list
```

### Base de Datos

```bash
# Conectar a PostgreSQL
psql -h <host> -U <user> -d <database>

# Backup
pg_dump -h <host> -U <user> -d <database> > backup.sql

# Restore
psql -h <host> -U <user> -d <database> < backup.sql

# Ver tamaño de BD
psql -h <host> -U <user> -d <database> -c "SELECT pg_size_pretty(pg_database_size('database_name'));"
```

---

## 📞 Escalación

### Cuándo escalar

- **P1 - Crítico**: Sistema completamente caído
- **P2 - Alto**: Funcionalidad principal afectada
- **P3 - Medio**: Funcionalidad secundaria afectada
- **P4 - Bajo**: Impacto mínimo

### Proceso de escalación

1. **Intentar resolver**: Usar esta guía para resolver
2. **Documentar**: Documentar intentos de resolución
3. **Escalar**: Contactar al equipo de plataforma
4. **Comunicar**: Notificar stakeholders si es necesario

### Contactos

- **Platform Team**: `#platform-support` en Slack
- **On-call**: Ver PagerDuty para on-call engineer
- **Documentación**: Ver [`docs/OPERACION.md`](./OPERACION.md)

---

## 📚 Recursos Adicionales

- [Kubernetes Troubleshooting](https://kubernetes.io/docs/tasks/debug/)
- [Airflow Troubleshooting](https://airflow.apache.org/docs/apache-airflow/stable/troubleshooting/index.html)
- [PostgreSQL Troubleshooting](https://www.postgresql.org/docs/current/runtime-config-logging.html)
- [Kubernetes Debugging](https://kubernetes.io/docs/tasks/debug-application-cluster/)

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

