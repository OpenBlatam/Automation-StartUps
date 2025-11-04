# Airbyte - Integración de Datos

Este documento describe la configuración y uso de Airbyte en la plataforma.

## Resumen

Airbyte es una plataforma open-source de integración de datos (ELT) con más de 600 conectores listos para sincronizar datos entre fuentes y destinos. Se integra con Airflow para orquestación de flujos complejos.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Airflow (Orquestación)                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  DAG: airbyte_sync.py                                 │  │
│  │  - Trigger sincronizaciones                           │  │
│  │  - Coordinar múltiples sources                        │  │
│  │  - Validación post-sync                               │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ API REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Airbyte Server (API + UI)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  WebApp: UI para configurar conexiones               │  │
│  │  Server: API REST para gestionar syncs                │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Airbyte Worker │    │  Airbyte Worker │    ...
│  (Sincronización)│   │  (Sincronización)│
└────────┬────────┘    └────────┬────────┘
         │                      │
         └───────────┬───────────┘
                    ▼
    ┌───────────────────────────────┐
    │  Sources: Stripe, HubSpot,    │
    │  PostgreSQL, APIs, etc.       │
    └───────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │  Destinations: Snowflake,     │
    │  PostgreSQL, S3, etc.         │
    └───────────────────────────────┘
```

## Componentes

### 1. WebApp

Interfaz web para:
- Configurar Sources (fuentes de datos)
- Configurar Destinations (destinos)
- Crear y gestionar Connections
- Monitorear sincronizaciones
- Ver logs y métricas

**Recursos**:
- CPU: 200m-1000m
- Memoria: 512Mi-1Gi
- Replicas: 2 (HA)

### 2. Server

API REST para:
- Gestión de conexiones
- Trigger de sincronizaciones
- Monitoreo de jobs
- Configuración programática

**Recursos**:
- CPU: 500m-2000m
- Memoria: 1Gi-2Gi
- Replicas: 2 (HA)

### 3. Workers

Ejecutan las sincronizaciones de datos:
- Leen de Sources
- Transforman (si aplica)
- Escriben a Destinations
- Auto-escalan según carga

**Recursos**:
- CPU: 500m-2000m
- Memoria: 1Gi-4Gi
- Replicas: 2-10 (HPA)

### 4. PostgreSQL

Base de datos interna de Airbyte para:
- Metadata de conexiones
- Estado de jobs
- Configuraciones
- Logs

**Storage**: 20Gi (ajustable)

### 5. MinIO (opcional)

S3-compatible storage para:
- Archivos temporales
- Cache de datos
- Staging de grandes volúmenes

**Storage**: 50Gi (ajustable)

## Despliegue

### Prerrequisitos

1. Namespace `integration` creado
2. Ingress controller (NGINX) instalado
3. Cert-manager para TLS (opcional)
4. Prometheus Operator para métricas (opcional)

### Paso 1: Aplicar Helm Chart

```bash
# Aplicar configuración de Airbyte
kubectl apply -f kubernetes/integration/airbyte.yaml

# Verificar que los pods se están creando
kubectl get pods -n integration -l app=airbyte -w
```

Esperar a que todos los pods estén `Running`:

```bash
# Verificar estado
kubectl get pods -n integration -l app=airbyte
```

Salida esperada:
```
NAME                            READY   STATUS    RESTARTS   AGE
airbyte-server-xxx              1/1     Running   0          2m
airbyte-webapp-xxx              1/1     Running   0          2m
airbyte-worker-xxx              1/1     Running   0          2m
airbyte-postgresql-xxx           1/1     Running   0          2m
airbyte-minio-xxx                1/1     Running   0          2m
```

### Paso 2: Configurar Ingress

```bash
# Editar airbyte-ingress.yaml y actualizar el host
# Cambiar "airbyte.example.com" por tu dominio

# Aplicar Ingress
kubectl apply -f kubernetes/ingress/airbyte-ingress.yaml

# Verificar Ingress
kubectl get ingress -n integration airbyte-ingress
```

### Paso 3: Configurar Secrets

**Opción A: External Secrets (Recomendado)**

Crear ExternalSecret para credenciales de Airbyte:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: airbyte-credentials
  namespace: integration
spec:
  secretStoreRef:
    name: aws-secrets-manager  # o azure-key-vault
    kind: SecretStore
  target:
    name: airbyte-secrets
  data:
    - secretKey: airbyte-password
      remoteRef:
        key: airbyte/api-password
    - secretKey: postgres-password
      remoteRef:
        key: airbyte/postgres-password
    - secretKey: minio-password
      remoteRef:
        key: airbyte/minio-password
```

**Opción B: Secret Manual**

```bash
kubectl create secret generic airbyte-secrets \
  --from-literal=airbyte-password='changeme' \
  --from-literal=postgres-password='changeme' \
  --from-literal=minio-password='changeme' \
  -n integration
```

Actualizar `airbyte.yaml` para usar el secret:

```yaml
global:
  postgresql:
    auth:
      existingSecret: airbyte-secrets
      secretKeys:
        postgresPasswordKey: postgres-password
```

### Paso 4: Configurar ServiceMonitor (Opcional)

```bash
kubectl apply -f observability/servicemonitors/airbyte.yaml
```

Verificar que Prometheus esté scrapeando:

```bash
kubectl port-forward -n observability service/prometheus 9090:9090
# Abrir http://localhost:9090
# Buscar: airbyte_server_*
```

## Configuración Inicial

### 1. Acceder a la UI

Abrir en navegador: `https://airbyte.example.com`

**Credenciales por defecto**:
- Usuario: `airbyte`
- Password: Configurado en secrets (o valor por defecto del Helm chart)

### 2. Crear Primer Source

1. Ir a **Sources** → **New Source**
2. Seleccionar fuente (ej: Stripe, PostgreSQL, HubSpot)
3. Configurar credenciales:
   - Usar External Secrets cuando sea posible
   - Para APIs: configurar API keys
   - Para databases: usar connection strings desde secrets
4. **Test Connection** para verificar
5. Guardar con nombre descriptivo

### 3. Crear Primer Destination

1. Ir a **Destinations** → **New Destination**
2. Seleccionar destino (ej: PostgreSQL, Snowflake, S3)
3. Configurar credenciales
4. **Test Connection**
5. Guardar

### 4. Crear Connection

1. Ir a **Connections** → **New Connection**
2. Seleccionar Source creado
3. Seleccionar Destination creado
4. Configurar:
   - **Sync Frequency**: Cada cuánto sincronizar
   - **Sync Mode**: Full refresh o Incremental
   - **Streams**: Qué tablas/streams incluir
   - **Namespace**: Esquema/namespace en destino
5. **Save & Run** para primera sincronización

### 5. Obtener Connection ID para Airflow

**Opción A: Desde UI**
- Abrir la conexión
- El Connection ID está en la URL: `/workspaces/.../connections/<CONNECTION_ID>`

**Opción B: Desde API**

```bash
# Obtener todas las conexiones
curl -u username:password \
  http://airbyte-server.integration.svc.cluster.local:8000/api/v1/connections/list

# Filtrar por nombre
curl -u username:password \
  http://airbyte-server.integration.svc.cluster.local:8000/api/v1/connections/list \
  | jq '.data[] | select(.name=="Stripe to PostgreSQL") | .connectionId'
```

## Integración con Airflow

Ver documentación completa en: `data/airflow/dags/README_AIRBYTE.md`

### Variables Requeridas

Configurar en Airflow (UI → Admin → Variables):

```python
AIRBYTE_API_URL = "http://airbyte-server.integration.svc.cluster.local:8000"
AIRBYTE_API_USERNAME = "airbyte"
AIRBYTE_API_PASSWORD = "<from-external-secrets>"
AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID = "<connection-id>"
```

### Ejemplo de DAG

```python
from airflow import DAG
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync

with DAG("my_airbyte_sync", ...) as dag:
    sync = PythonOperator(
        task_id="sync_stripe",
        python_callable=trigger_airbyte_sync,
        op_kwargs={"connection_id": "{{ var.value.AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID }}"},
    )
```

## Monitoreo

### Métricas Prometheus

Métricas disponibles en `/metrics`:

- `airbyte_server_job_succeeded_total`: Jobs exitosos
- `airbyte_server_job_failed_total`: Jobs fallidos
- `airbyte_server_job_duration_seconds`: Duración de jobs
- `airbyte_worker_active_jobs`: Jobs activos por worker

### Dashboards Grafana

Crear dashboard con métricas de:
- Tasa de éxito/fallo de sincronizaciones
- Duración promedio de jobs
- Uso de recursos (CPU/memoria) de workers
- Throughput (registros procesados por segundo)

### Logs

```bash
# Logs del servidor
kubectl logs -n integration -l app=airbyte,component=server --tail=100

# Logs de workers
kubectl logs -n integration -l app=airbyte,component=worker --tail=100

# Logs de una sincronización específica
# Buscar en la UI de Airbyte → Connections → Ver logs
```

## Auto-escalado

El HPA escala workers automáticamente:

```yaml
# Configurado en airbyte.yaml
minReplicas: 2
maxReplicas: 10
metrics:
  - cpu: 70%
  - memory: 80%
```

Ver estado:

```bash
kubectl get hpa -n integration airbyte-worker-hpa
```

## Troubleshooting

### Problema: Pods no inician

```bash
# Verificar eventos
kubectl describe pod -n integration <pod-name>

# Verificar PVCs (PersistentVolumeClaims)
kubectl get pvc -n integration

# Verificar recursos disponibles
kubectl top nodes
```

### Problema: Sincronización falla

1. Ver logs en UI de Airbyte
2. Verificar credenciales en Source/Destination
3. Verificar conectividad de red (NetworkPolicies)
4. Verificar recursos disponibles en workers

### Problema: Worker out of memory

Aumentar límites de memoria en `airbyte.yaml`:

```yaml
worker:
  resources:
    limits:
      memory: 8Gi  # Aumentar según necesidad
```

### Problema: Sincronización lenta

1. Verificar recursos de workers: `kubectl top pods -n integration`
2. Escalar workers manualmente:
   ```bash
   kubectl scale deployment airbyte-worker -n integration --replicas=5
   ```
3. Verificar velocidad de red a Source/Destination
4. Considerar aumentar CPU límites

### Problema: No puedo acceder a la UI

```bash
# Verificar Ingress
kubectl get ingress -n integration airbyte-ingress

# Verificar servicios
kubectl get svc -n integration -l app=airbyte

# Port-forward para testing
kubectl port-forward -n integration svc/airbyte-webapp 8080:80
# Abrir http://localhost:8080
```

## Mejores Prácticas

1. **Secrets Management**: Usar External Secrets para todas las credenciales
2. **Monitoreo**: Configurar alertas en Grafana para jobs fallidos
3. **Backup**: Hacer backup de PostgreSQL de Airbyte periódicamente
4. **Recursos**: Ajustar recursos según volumen de datos
5. **NetworkPolicies**: Restringir tráfico de red según necesidad
6. **Actualizaciones**: Seguir releases de Airbyte Helm chart
7. **Orquestación**: Usar Airflow para flujos complejos, Airbyte para sincronizaciones simples

## Top 10 Conectores Más Útiles

Ver `AIRBYTE_TOP_CONNECTORS.md` para la lista completa de los 10 conectores más útiles con:
- Descripción detallada
- Casos de uso específicos
- Configuración típica
- Ventajas de cada conector

**Top 3**:
1. **PostgreSQL** - Database (Source & Destination)
2. **Stripe** - Payment Processing (Source)
3. **HubSpot** - CRM (Source)

## Referencias

### Documentación Externa

- [Documentación oficial de Airbyte](https://docs.airbyte.com/)
- [Airbyte Helm Chart](https://github.com/airbytehq/airbyte-helm-charts)
- [Lista de conectores](https://docs.airbyte.com/integrations/)
- [API Reference](https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html)
- [Troubleshooting Guide](https://docs.airbyte.com/troubleshooting/)

### Documentación Interna

- **Guía de integración con Airflow**: `data/airflow/dags/README_AIRBYTE.md`
- **Top 10 Conectores**: `AIRBYTE_TOP_CONNECTORS.md` (guía completa con configuraciones)
- **Arquitecturas y Ejemplos**: `AIRBYTE_ARCHITECTURE_EXAMPLES.md` (diagramas y patterns)
- **Mejoras Implementadas**: `IMPROVEMENTS_AIRBYTE.md`
- **Quick Start**: `QUICK_START_AIRBYTE.md`

