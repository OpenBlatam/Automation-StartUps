# 🚀 Funcionalidades Avanzadas V3 - Sistema de Backups

## Nuevas Características Implementadas

### 1. 📅 Scheduler Inteligente (`backup_scheduler.py`)

Programación adaptativa basada en carga del sistema:

```python
from data.airflow.plugins.backup_scheduler import (
    IntelligentBackupScheduler,
    BackupSchedule,
    BackupPriority
)

scheduler = IntelligentBackupScheduler()

# Crear schedule de backup
schedule = BackupSchedule(
    backup_id="db-backup-prod",
    priority=BackupPriority.CRITICAL,
    preferred_window_start=2,  # 2 AM
    preferred_window_end=6,     # 6 AM
    max_delay_hours=6,
    estimated_duration_minutes=45,
    resources_required={'cpu': 0.3, 'memory': 0.5}
)

scheduler.add_schedule(schedule)

# Obtener tiempo óptimo
optimal_time = scheduler.get_optimal_time(schedule)
print(f"Optimal backup time: {optimal_time}")

# Programar múltiples backups
schedules = [schedule1, schedule2, schedule3]
scheduled = scheduler.schedule_backups(schedules)

# Obtener estadísticas de carga
load_stats = scheduler.get_load_statistics()
```

**Características:**
- Detecta ventanas de bajo uso
- Evita horas pico
- Respeta prioridades
- Balancea carga de backups
- Monitorea CPU, memoria y disco

### 2. 🔑 Rotación de Claves (`backup_key_rotation.py`)

Rotación automática de claves de encriptación:

```python
from data.airflow.plugins.backup_key_rotation import BackupKeyRotator
from data.airflow.plugins.backup_encryption import BackupEncryption

rotator = BackupKeyRotator(
    backup_dir="/tmp/backups",
    key_storage_dir="/tmp/backup-keys"
)

# Cargar clave actual
old_key = BackupEncryption.load_key_from_env()

# Rotar claves y re-encriptar backups
result = rotator.rotate_keys(
    old_key=old_key,
    new_key=None,  # Generar nueva automáticamente
    reencrypt_backups=True,
    days_back=90  # Re-encriptar últimos 90 días
)

print(f"Rotated {result.backups_reencrypted} backups")
print(f"Failed: {result.backups_failed}")

# Listar claves almacenadas
keys = rotator.list_keys()
for key_info in keys:
    print(f"Key {key_info['key_id']}: {key_info['metadata']}")
```

**Características:**
- Generación automática de nuevas claves
- Re-encriptación de backups antiguos
- Gestión de múltiples claves
- Metadatos de claves
- Almacenamiento seguro

**Uso en DAG:**
```python
@task(task_id='rotate_encryption_keys')
def rotate_keys():
    """Rota claves de encriptación mensualmente."""
    rotator = BackupKeyRotator()
    old_key = BackupEncryption.load_key_from_env()
    
    result = rotator.rotate_keys(
        old_key=old_key,
        reencrypt_backups=True,
        days_back=30
    )
    
    if result.error:
        raise Exception(f"Key rotation failed: {result.error}")
    
    return result
```

### 3. 📊 Métricas de Prometheus (`backup_prometheus.py`)

Exportación de métricas a Prometheus:

```python
from data.airflow.plugins.backup_prometheus import get_backup_metrics

metrics = get_backup_metrics()

# Registrar backup
metrics.record_backup(
    backup_type='database',
    status='completed',
    duration_seconds=45.2,
    size_bytes=1024*1024*100,  # 100 MB
    encryption_time=2.1,
    upload_time=12.5,
    cloud_provider='aws'
)

# Actualizar tasas de éxito
metrics.update_success_rate('database', 0.95)

# Actualizar tamaño total
metrics.update_total_size('database', 1024*1024*1024*10)  # 10 GB

# Registrar verificación
metrics.record_verification('passed')

# Registrar restauración
metrics.record_restore('completed')

# Actualizar salud
metrics.update_health_status('disk_space', True)
metrics.update_health_status('encryption', True)

# Actualizar métricas de disco
metrics.update_disk_metrics(usage_percent=75.5, free_bytes=50*1024*1024*1024)

# Obtener métricas en formato Prometheus
prometheus_metrics = metrics.get_metrics()
```

**Métricas Disponibles:**

#### Contadores
- `backup_total{type, status}` - Total de backups
- `backup_errors_total{error_type}` - Total de errores
- `backup_verification_total{status}` - Total de verificaciones
- `backup_restore_total{status}` - Total de restauraciones

#### Histogramas
- `backup_duration_seconds{type, status}` - Duración de backups
- `backup_size_bytes{type}` - Tamaño de backups
- `backup_encryption_time_seconds` - Tiempo de encriptación
- `backup_upload_time_seconds{cloud_provider}` - Tiempo de subida

#### Gauges
- `backup_success_rate{type}` - Tasa de éxito
- `backup_total_size_bytes{type}` - Tamaño total
- `backup_health_status{check_type}` - Estado de salud
- `backup_disk_usage_percent` - Uso de disco
- `backup_disk_free_bytes` - Espacio libre

**Endpoint de Métricas:**

```python
from flask import Flask
from data.airflow.plugins.backup_prometheus import get_backup_metrics

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    """Endpoint de métricas de Prometheus."""
    metrics = get_backup_metrics()
    return metrics.get_metrics(), 200, {'Content-Type': 'text/plain'}
```

**Configuración de Prometheus:**

```yaml
scrape_configs:
  - job_name: 'backups'
    scrape_interval: 30s
    static_configs:
      - targets: ['backup-api:5000']
    metrics_path: '/metrics'
```

**Grafana Dashboard:**

Usar métricas para crear dashboards:
- Tasa de éxito de backups
- Tamaño total de backups
- Tiempo promedio de backups
- Uso de disco
- Estado de salud

### 4. 🔄 Integración Completa

#### En BackupManager

Las métricas se registran automáticamente:

```python
# Automáticamente registra en Prometheus
result = manager.backup_database(...)
# Métricas ya registradas
```

#### En DAGs

```python
from data.airflow.plugins.backup_prometheus import get_backup_metrics

@task
def update_metrics():
    """Actualiza métricas desde el manager."""
    metrics_obj = get_backup_metrics()
    manager_metrics = manager.get_metrics()
    
    metrics_obj.update_success_rate('database', manager_metrics['success_rate'])
    metrics_obj.update_total_size('database', manager_metrics['total_size_bytes'])
```

### 5. 📈 Ejemplos de Uso

#### Scheduler en DAG

```python
@dag(...)
def scheduled_backups():
    scheduler = IntelligentBackupScheduler()
    
    @task
    def schedule_database_backups():
        schedule = BackupSchedule(
            backup_id="db-prod",
            priority=BackupPriority.CRITICAL,
            preferred_window_start=2,
            preferred_window_end=6
        )
        scheduler.add_schedule(schedule)
        optimal_time = scheduler.get_optimal_time(schedule)
        return optimal_time.isoformat()
    
    @task
    def execute_backup(scheduled_time):
        # Ejecutar backup en tiempo óptimo
        return manager.backup_database(...)
```

#### Rotación Mensual

```python
@dag(
    schedule='0 0 1 * *',  # Primer día del mes
    ...
)
def monthly_key_rotation():
    @task
    def rotate_keys():
        rotator = BackupKeyRotator()
        old_key = BackupEncryption.load_key_from_env()
        return rotator.rotate_keys(old_key, reencrypt_backups=True)
```

#### Endpoint de Métricas

```python
# En backup_api.py
@app.route('/metrics')
def prometheus_metrics():
    """Endpoint de métricas de Prometheus."""
    from data.airflow.plugins.backup_prometheus import get_backup_metrics
    metrics = get_backup_metrics()
    return metrics.get_metrics(), 200, {'Content-Type': 'text/plain'}
```

## Resumen de Nuevas Funcionalidades

1. ✅ **Scheduler Inteligente** - Programación adaptativa
2. ✅ **Rotación de Claves** - Seguridad mejorada
3. ✅ **Métricas de Prometheus** - Monitoreo completo
4. ✅ **Integración Automática** - Métricas registradas automáticamente

## Dependencias Nuevas

```txt
prometheus-client  # Métricas de Prometheus
```

## Configuración

### Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'backups'
    static_configs:
      - targets: ['backup-api:5000']
```

### Grafana

Importar dashboard desde métricas de Prometheus:
- Backup success rate
- Backup duration
- Backup size
- Disk usage
- Health status

## Beneficios

1. **Programación Inteligente** - Mejor uso de recursos
2. **Seguridad Mejorada** - Rotación de claves
3. **Monitoreo Completo** - Métricas en tiempo real
4. **Dashboards** - Visualización de métricas

¡Sistema de backups completo con todas las funcionalidades avanzadas! 🚀

