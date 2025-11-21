# 🚀 Funcionalidades Avanzadas del Sistema de Backups

## Nuevas Características Implementadas

### 1. 🔄 Restauración de Backups

Módulo completo para restaurar backups:

```python
from data.airflow.plugins.backup_restore import BackupRestorer
from data.airflow.plugins.backup_encryption import BackupEncryption

# Cargar clave de encriptación
encryption_key = BackupEncryption.load_key_from_env()

# Crear restaurador
restorer = BackupRestorer(
    backup_dir="/tmp/backups",
    encryption_key=encryption_key
)

# Verificar backup antes de restaurar
is_valid, error = restorer.verify_backup("backup.sql.gz.encrypted")
if not is_valid:
    print(f"Backup inválido: {error}")
    return

# Restaurar base de datos
result = restorer.restore_database(
    backup_path="backup.sql.gz.encrypted",
    connection_string="postgresql://user:pass@host:5432/db",
    db_type="postgresql",
    drop_existing=False,
    verify_backup=True
)

if result.status.value == 'completed':
    print(f"✅ Restauración completada en {result.duration_seconds:.2f}s")
else:
    print(f"❌ Error: {result.error}")

# Restaurar archivos
result = restorer.restore_files(
    backup_path="files.tar.gz.encrypted",
    target_dir="/tmp/restored",
    verify_backup=True
)
```

**Características:**
- Verificación automática antes de restaurar
- Desencriptación y descompresión automáticas
- Soporte para PostgreSQL y MySQL
- Restauración de archivos desde tar.gz

### 2. 📊 Analytics y Reportes

Sistema completo de analytics:

```python
from data.airflow.plugins.backup_analytics import BackupAnalyticsEngine

engine = BackupAnalyticsEngine(backup_dir="/tmp/backups")

# Reporte diario
daily_report = engine.generate_daily_report()

# Reporte semanal
weekly_report = engine.generate_weekly_report()

# Reporte mensual
monthly_report = engine.generate_monthly_report()

# Predicción de espacio
prediction = engine.predict_space_needs(days=30)
print(f"Espacio estimado para próximos 30 días: {prediction['predicted_size_gb']:.2f} GB")
```

**DAG Automático:**
- `backup_analytics_report`: Genera reportes automáticamente
  - Diario: 8 AM
  - Semanal: Domingos
  - Mensual: Día 1 de cada mes

### 3. ✅ Verificación Automática

Verificación de integridad de backups:

```python
from data.airflow.plugins.backup_verification import BackupVerifier

verifier = BackupVerifier(
    backup_dir="/tmp/backups",
    encryption_key=encryption_key
)

# Verificar un backup específico
result = verifier.verify_backup(
    backup_path="backup.sql.gz.encrypted",
    verify_checksum=True,
    verify_encryption=True,
    verify_compression=True,
    test_restore=False  # Opcional: hacer test de restauración
)

if result.status.value == 'passed':
    print("✅ Backup verificado correctamente")
else:
    print(f"❌ Errores: {result.errors}")

# Verificar todos los backups recientes
results = verifier.verify_all_recent_backups(days=7)
report = verifier.generate_verification_report(results)
```

**DAG Automático:**
- `backup_verification`: Verifica backups diariamente a las 6 AM
- Verifica backups de últimos 7 días
- Verifica backups críticos (últimas 24h)
- Alertas automáticas si hay fallos

### 4. 📋 Listado de Backups Disponibles

```python
restorer = BackupRestorer()

# Listar backups disponibles
backups = restorer.list_available_backups(
    backup_type='db',  # 'db', 'files', o None para todos
    days=30
)

for backup in backups:
    print(f"{backup['name']}: {backup['size'] / (1024**2):.2f} MB - {backup['modified']}")
```

## DAGs Nuevos

### 1. `backup_analytics_report`
- **Frecuencia**: Diario (8 AM)
- **Funciones**:
  - Reporte diario
  - Reporte semanal (domingos)
  - Reporte mensual (día 1)
  - Predicción de espacio

### 2. `backup_verification`
- **Frecuencia**: Diario (6 AM)
- **Funciones**:
  - Verificación de backups recientes
  - Verificación de backups críticos
  - Alertas automáticas

## Casos de Uso Avanzados

### Restauración de Emergencia

```python
# 1. Listar backups disponibles
restorer = BackupRestorer()
backups = restorer.list_available_backups(backup_type='db', days=7)

# 2. Seleccionar backup más reciente
latest_backup = backups[0]  # Ya están ordenados por fecha

# 3. Verificar integridad
verifier = BackupVerifier()
verification = verifier.verify_backup(latest_backup['path'])

if verification.status.value == 'passed':
    # 4. Restaurar
    result = restorer.restore_database(
        backup_path=latest_backup['path'],
        connection_string="postgresql://user:pass@host:5432/db",
        db_type="postgresql"
    )
```

### Monitoreo de Integridad

```python
# En un DAG personalizado
@task
def monitor_backup_integrity():
    verifier = BackupVerifier()
    results = verifier.verify_all_recent_backups(days=7)
    
    report = verifier.generate_verification_report(results)
    
    # Alertar si tasa de éxito < 95%
    if report['pass_rate'] < 0.95:
        send_critical_alert(f"Backup integrity below threshold: {report['pass_rate']:.1%}")
    
    return report
```

### Planificación de Espacio

```python
engine = BackupAnalyticsEngine()

# Predecir necesidades futuras
prediction = engine.predict_space_needs(days=90)

if prediction['predicted_size_gb'] > available_space_gb:
    # Alertar sobre necesidad de más espacio
    send_alert(f"Predicted space needs ({prediction['predicted_size_gb']:.2f}GB) exceed available space")
```

### Reportes Personalizados

```python
# Generar reporte personalizado
engine = BackupAnalyticsEngine()

# Reporte de últimos 30 días
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
backups = engine._get_backups_in_range(start_date, end_date)
analytics = engine._calculate_analytics(backups, start_date, end_date)

# Enviar a sistema de BI
send_to_bi_system(analytics)
```

## Integración con Otros Sistemas

### Prometheus Metrics

```python
from prometheus_client import Gauge

backup_success_rate = Gauge('backup_success_rate', 'Backup success rate')
backup_total_size = Gauge('backup_total_size_gb', 'Total backup size in GB')

# En el DAG
metrics = manager.get_metrics()
backup_success_rate.set(metrics['success_rate'])
backup_total_size.set(metrics['total_size_bytes'] / (1024**3))
```

### Grafana Dashboard

Usar métricas de Prometheus para crear dashboards:
- Tasa de éxito de backups
- Tamaño total de backups
- Tiempo promedio de backups
- Espacio usado vs disponible

## Mejores Prácticas

### 1. Verificación Regular

```python
# Verificar backups críticos diariamente
# Verificar todos los backups semanalmente
```

### 2. Tests de Restauración

```python
# Hacer test de restauración mensualmente en ambiente de prueba
result = restorer.restore_database(
    backup_path="backup.sql.gz.encrypted",
    connection_string="postgresql://user:pass@test-db:5432/test_db",
    db_type="postgresql",
    test_restore=True
)
```

### 3. Monitoreo Proactivo

```python
# Monitorear predicciones de espacio
# Alertar antes de quedarse sin espacio
```

### 4. Reportes Regulares

```python
# Revisar reportes semanales y mensuales
# Ajustar políticas de retención según necesidades
```

## Troubleshooting

### Backup no se puede restaurar

1. Verificar que el backup existe
2. Verificar que la clave de encriptación es correcta
3. Verificar integridad: `verifier.verify_backup(backup_path)`
4. Verificar logs de restauración

### Verificación falla

1. Verificar que el archivo .checksum existe
2. Verificar que la clave de encriptación es correcta
3. Verificar que el archivo no está corrupto

### Predicción de espacio incorrecta

1. Verificar que hay suficientes datos históricos (mínimo 7 días)
2. Ajustar parámetros de predicción
3. Revisar tendencias de crecimiento

## Ejemplo Completo

```python
from data.airflow.plugins.backup_manager import BackupManager, BackupConfig
from data.airflow.plugins.backup_restore import BackupRestorer
from data.airflow.plugins.backup_verification import BackupVerifier
from data.airflow.plugins.backup_analytics import BackupAnalyticsEngine
from data.airflow.plugins.backup_encryption import BackupEncryption

# 1. Configurar
encryption_key = BackupEncryption.load_key_from_env()
manager = BackupManager(encryption_key=encryption_key)
restorer = BackupRestorer(encryption_key=encryption_key)
verifier = BackupVerifier(encryption_key=encryption_key)
analytics = BackupAnalyticsEngine()

# 2. Crear backup
result = manager.backup_database(
    connection_string="postgresql://...",
    config=BackupConfig(encrypt=True, compress=True)
)

# 3. Verificar backup
verification = verifier.verify_backup(result.file_path)
assert verification.status.value == 'passed'

# 4. Generar analytics
report = analytics.generate_daily_report()

# 5. Si es necesario restaurar
if needed:
    restore_result = restorer.restore_database(
        backup_path=result.file_path,
        connection_string="postgresql://...",
        db_type="postgresql"
    )
```

## Resumen de Módulos

1. **backup_manager.py** - Gestión de backups
2. **backup_encryption.py** - Encriptación
3. **backup_notifications.py** - Alertas
4. **backup_health.py** - Health checks
5. **backup_restore.py** - Restauración ⭐ NUEVO
6. **backup_analytics.py** - Analytics ⭐ NUEVO
7. **backup_verification.py** - Verificación ⭐ NUEVO

Sistema completo de backups con todas las funcionalidades necesarias para producción! 🚀

