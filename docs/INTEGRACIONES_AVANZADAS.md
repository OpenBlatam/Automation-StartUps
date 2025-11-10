# 🔗 Integraciones Avanzadas del Sistema de Backups

## Nuevas Integraciones Implementadas

### 1. 📦 Backup de Volúmenes Persistentes (`backup_volume_snapshots.py`)

Backup de volúmenes persistentes de Kubernetes:

```python
from data.airflow.plugins.backup_volume_snapshots import KubernetesVolumeSnapshotter

snapshotter = KubernetesVolumeSnapshotter()

# Listar volúmenes
volumes = snapshotter.list_persistent_volumes(namespace="production")

# Crear snapshot
snapshot = snapshotter.create_volume_snapshot(
    volume_name="data-pvc",
    namespace="production",
    snapshot_name="snapshot-data-20250115"
)

# Backup de datos del volumen
backup_result = snapshotter.backup_volume_data(
    volume_name="data-pvc",
    namespace="production",
    output_path="/tmp/volume-backup.tar.gz"
)
```

**Características:**
- Snapshot de PersistentVolumes
- Backup de datos de volúmenes
- Soporte para VolumeSnapshot API
- Backup desde pods que montan volúmenes

### 2. 🚨 Integración con Sistemas de Alertas (`backup_alerting_integrations.py`)

Integración con múltiples sistemas de alertas:

#### PagerDuty

```python
from data.airflow.plugins.backup_alerting_integrations import (
    PagerDutyIntegration,
    Alert,
    AlertSeverity
)

pagerduty = PagerDutyIntegration(
    integration_key=os.getenv("PAGERDUTY_INTEGRATION_KEY")
)

alert = Alert(
    title="Backup Failed",
    message="Critical backup failed",
    severity=AlertSeverity.CRITICAL,
    details={"backup_id": "backup-123"}
)

pagerduty.send_alert(alert)
```

#### Opsgenie

```python
from data.airflow.plugins.backup_alerting_integrations import OpsgenieIntegration

opsgenie = OpsgenieIntegration(
    api_key=os.getenv("OPSGENIE_API_KEY")
)

opsgenie.send_alert(alert)
```

#### Datadog

```python
from data.airflow.plugins.backup_alerting_integrations import DatadogIntegration

datadog = DatadogIntegration(
    api_key=os.getenv("DATADOG_API_KEY"),
    app_key=os.getenv("DATADOG_APP_KEY")
)

datadog.send_alert(alert)
```

#### Gestor Multi-Canal

```python
from data.airflow.plugins.backup_alerting_integrations import MultiAlertManager

alert_manager = MultiAlertManager()

# Enviar a todos los canales configurados
results = alert_manager.send_alert(alert)

# Enviar a canales específicos
results = alert_manager.send_alert(
    alert,
    channels=['pagerduty', 'opsgenie']
)

# Métodos de conveniencia
alert_manager.send_backup_failure_alert(
    backup_id="backup-123",
    error="Connection timeout"
)

alert_manager.send_critical_alert(
    title="System Critical",
    message="Backup system is down"
)
```

### 3. 🗄️ Backup de Bases de Datos NoSQL (`backup_nosql.py`)

Backup de bases de datos NoSQL:

#### MongoDB

```python
from data.airflow.plugins.backup_nosql import NoSQLBackup

nosql = NoSQLBackup()

# Backup de todas las bases de datos
result = nosql.backup_mongodb(
    connection_string="mongodb://user:pass@host:27017",
    output_path="/tmp/mongodb-backup"
)

# Backup de base de datos específica
result = nosql.backup_mongodb(
    connection_string="mongodb://user:pass@host:27017",
    database="production",
    output_path="/tmp/mongodb-backup"
)
```

#### Redis

```python
# Backup de Redis
result = nosql.backup_redis(
    host="localhost",
    port=6379,
    password="password",
    output_path="/tmp/redis-backup.rdb"
)
```

#### Elasticsearch

```python
# Backup de Elasticsearch
result = nosql.backup_elasticsearch(
    host="localhost",
    port=9200,
    indices=["logs", "metrics"],  # None = todos
    output_path="/tmp/elasticsearch-backup"
)
```

#### Cassandra

```python
# Backup de Cassandra
result = nosql.backup_cassandra(
    host="localhost",
    keyspace="production",  # None = todos
    output_path="/tmp/cassandra-backup"
)
```

## Configuración

### Variables de Entorno

```bash
# PagerDuty
export PAGERDUTY_INTEGRATION_KEY="your-integration-key"

# Opsgenie
export OPSGENIE_API_KEY="your-api-key"

# Datadog
export DATADOG_API_KEY="your-api-key"
export DATADOG_APP_KEY="your-app-key"

# MongoDB
export MONGODB_CONNECTION_STRING="mongodb://user:pass@host:27017"

# Redis
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_PASSWORD="password"

# Elasticsearch
export ELASTICSEARCH_HOST="localhost"
export ELASTICSEARCH_PORT="9200"
```

## Uso en DAGs

### Integración con Alertas

```python
from data.airflow.plugins.backup_alerting_integrations import MultiAlertManager

@task
def backup_with_alerts():
    manager = BackupManager(...)
    result = manager.backup_database(...)
    
    if result.status.value == 'failed':
        alert_manager = MultiAlertManager()
        alert_manager.send_backup_failure_alert(
            backup_id=result.backup_id,
            error=result.error
        )
    
    return result
```

### Backup de NoSQL

```python
@dag(...)
def nosql_backups():
    @task
    def backup_mongodb():
        nosql = NoSQLBackup()
        return nosql.backup_mongodb(
            connection_string=os.getenv("MONGODB_CONNECTION_STRING")
        )
    
    @task
    def backup_redis():
        nosql = NoSQLBackup()
        return nosql.backup_redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT", "6379"))
        )
```

## Beneficios

1. **Alertas Multi-Canal** - Integración con sistemas profesionales
2. **NoSQL Support** - Backup de bases de datos modernas
3. **Kubernetes Volumes** - Backup de datos persistentes
4. **Integración Completa** - Sistema unificado

## Próximos Pasos

1. Configurar API keys de sistemas de alertas
2. Crear DAGs para backups NoSQL
3. Configurar snapshots de volúmenes
4. Integrar con sistemas de monitoreo existentes

¡Sistema de backups con integraciones completas! 🚀

