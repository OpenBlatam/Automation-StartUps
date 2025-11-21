# Quick Start - Airbyte

Guía rápida para desplegar y usar Airbyte en la plataforma.

## Despliegue Rápido

### 1. Aplicar Manifests

```bash
# Aplicar Airbyte
kubectl apply -f kubernetes/integration/airbyte.yaml

# Aplicar Ingress (actualizar hostname primero)
kubectl apply -f kubernetes/ingress/airbyte-ingress.yaml

# Esperar a que los pods estén listos
kubectl wait --for=condition=ready pod -l app=airbyte -n integration --timeout=300s
```

### 2. Configurar Secrets

```bash
# Crear secret con credenciales
kubectl create secret generic airbyte-secrets \
  --from-literal=airbyte-password='your-secure-password' \
  --from-literal=postgres-password='your-postgres-password' \
  --from-literal=minio-password='your-minio-password' \
  -n integration
```

### 3. Acceder a la UI

```bash
# Obtener la URL desde Ingress
kubectl get ingress -n integration airbyte-ingress

# O usar port-forward
kubectl port-forward -n integration svc/airbyte-webapp 8080:80
# Abrir http://localhost:8080
```

**Credenciales por defecto**:
- Usuario: `airbyte`
- Password: Configurado en secrets

## Primeras Conexiones

### 1. Crear Source: PostgreSQL

1. **Sources** → **New Source** → **PostgreSQL**
2. Configurar:
   - **Host**: `postgres.example.com`
   - **Port**: `5432`
   - **Database**: `mydb`
   - **Username**: Desde External Secrets
   - **Password**: Desde External Secrets
3. **Test Connection** → **Save**

### 2. Crear Destination: Snowflake

1. **Destinations** → **New Destination** → **Snowflake**
2. Configurar credenciales
3. **Test Connection** → **Save**

### 3. Crear Connection

1. **Connections** → **New Connection**
2. Seleccionar Source y Destination
3. Configurar:
   - **Sync Frequency**: `Every 6 hours`
   - **Sync Mode**: `Incremental` (si aplica)
   - **Streams**: Seleccionar tablas a sincronizar
4. **Save & Run**

## Integración con Airflow

### 1. Configurar Variables

En Airflow UI → **Admin** → **Variables**:

```python
AIRBYTE_API_URL = "http://airbyte-server.integration.svc.cluster.local:8000"
AIRBYTE_API_USERNAME = "airbyte"
AIRBYTE_API_PASSWORD = "<from-secrets>"
AIRBYTE_MY_CONNECTION_ID = "<connection-id-from-airbyte>"
```

### 2. Usar DAG Existente

El DAG `airbyte_stripe_to_postgres` está listo para usar:

1. Actualizar variable `AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID`
2. Habilitar DAG en Airflow UI
3. El DAG se ejecutará cada 6 horas automáticamente

### 3. Crear DAG Personalizado

```python
from airflow import DAG
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync
from airflow.operators.python import PythonOperator

with DAG("my_airbyte_sync", ...) as dag:
    sync = PythonOperator(
        task_id="sync_data",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": "{{ var.value.AIRBYTE_MY_CONNECTION_ID }}"
        },
    )
```

## Verificar Funcionamiento

```bash
# Ver pods de Airbyte
kubectl get pods -n integration -l app=airbyte

# Ver logs de una sincronización
kubectl logs -n integration -l app=airbyte,component=worker --tail=50

# Ver métricas
kubectl port-forward -n observability svc/prometheus 9090:9090
# Buscar métricas: airbyte_server_*
```

## Próximos Pasos

- Ver documentación completa: `README_AIRBYTE.md`
- Ver ejemplos de DAGs: `data/airflow/dags/README_AIRBYTE.md`
- Explorar conectores: https://docs.airbyte.com/integrations/
- Configurar External Secrets para credenciales





