# 🤖 Machine Learning y Backups de Configuraciones

## Nuevas Funcionalidades Implementadas

### 1. 🧠 Machine Learning para Predicción (`backup_ml_predictions.py`)

Predicción inteligente de fallos y análisis de anomalías:

```python
from data.airflow.plugins.backup_ml_predictions import BackupMLPredictor

predictor = BackupMLPredictor()

# Entrenar modelo con datos históricos
historical_data = [
    {
        'backup_id': 'backup-1',
        'status': 'completed',
        'duration_seconds': 120,
        'size_bytes': 1024*1024*100,
        'hour_of_day': 2,
        'day_of_week': 1,
        'previous_success_rate': 0.95
    },
    # ... más datos históricos
]

predictor.train_failure_prediction_model(historical_data)

# Predecir fallo de backup
prediction = predictor.predict_backup_failure(
    backup_config={
        'backup_id': 'backup-123',
        'estimated_duration': 300,
        'estimated_size': 1024*1024*500,
        'database_size_gb': 50
    },
    historical_context={
        'success_rate': 0.92,
        'recent_failures': 1
    }
)

print(f"Failure probability: {prediction.failure_probability:.2%}")
print(f"Risk factors: {prediction.risk_factors}")
print(f"Recommendations: {prediction.recommended_actions}")
```

**Detección de Anomalías:**

```python
# Detectar anomalías en métricas
baseline = {
    'duration_seconds': (120.0, 30.0),  # mean, std
    'size_bytes': (1024*1024*100, 1024*1024*20)
}

current_metrics = {
    'duration_seconds': 300.0,
    'size_bytes': 1024*1024*200
}

anomalies = predictor.detect_anomalies(current_metrics, baseline)

for anomaly in anomalies:
    if anomaly.is_anomaly:
        print(f"Anomaly detected in {anomaly.metric_name}: {anomaly.anomaly_score:.2f}")
```

**Predicción de Espacio con ML:**

```python
historical_sizes = [10.5, 11.2, 12.1, 13.0, 13.8, 14.5, 15.2]  # GB

prediction = predictor.predict_space_needs_ml(
    historical_sizes=historical_sizes,
    days_ahead=30
)

print(f"Predicted: {prediction['predicted_size_gb']:.2f} GB")
print(f"Confidence: {prediction['confidence']}")
print(f"Trend: {prediction.get('trend', 'unknown')}")
```

### 2. ⚙️ Backup de Configuraciones (`backup_config_backup.py`)

Backup automático de configuraciones:

```python
from data.airflow.plugins.backup_config_backup import ConfigurationBackup
from data.airflow.plugins.backup_encryption import BackupEncryption

encryption_key = BackupEncryption.load_key_from_env()
config_backup = ConfigurationBackup(encryption_key=encryption_key)

# Backup de variables de entorno
env_backup = config_backup.backup_environment_variables(
    env_prefix="APP_",
    sensitive_keys=['PASSWORD', 'SECRET', 'API_KEY']
)

# Backup de archivo de configuración
file_backup = config_backup.backup_config_file(
    config_path="/etc/app/config.yaml",
    config_format="yaml"
)

# Backup de configuración de aplicación
app_backup = config_backup.backup_application_config(
    app_name="myapp",
    config_data={
        'database_url': 'postgresql://...',
        'api_key': 'secret-key',
        'timeout': 30
    },
    encrypt_sensitive=True
)

# Listar backups
backups = config_backup.list_config_backups(
    config_type='env',
    days=30
)
```

**DAG Automático:**
- `config_backups`: Backups diarios de configuraciones a la 1 AM
  - Variables de entorno
  - Archivos de configuración
  - Configuraciones de aplicaciones

## Casos de Uso

### Predicción Proactiva de Fallos

```python
@task
def predict_backup_failure():
    """Predice fallos antes de ejecutar backup."""
    predictor = BackupMLPredictor()
    
    prediction = predictor.predict_backup_failure(
        backup_config={
            'estimated_duration': 300,
            'estimated_size': 1024*1024*100
        },
        historical_context={
            'success_rate': 0.95,
            'recent_failures': 0
        }
    )
    
    if prediction.failure_probability > 0.5:
        # Enviar alerta preventiva
        send_preventive_alert(prediction)
        # Considerar acciones alternativas
        return {'action': 'delay_or_manual', 'reason': prediction.risk_factors}
    
    return {'action': 'proceed', 'confidence': prediction.confidence}
```

### Detección de Anomalías en Tiempo Real

```python
@task
def monitor_backup_anomalies():
    """Monitorea anomalías en backups."""
    predictor = BackupMLPredictor()
    
    # Obtener métricas actuales
    current_metrics = {
        'duration_seconds': 180,
        'size_bytes': 1024*1024*150
    }
    
    # Obtener baseline histórico
    baseline = get_historical_baseline()
    
    # Detectar anomalías
    anomalies = predictor.detect_anomalies(current_metrics, baseline)
    
    critical_anomalies = [a for a in anomalies if a.severity == 'critical']
    if critical_anomalies:
        send_alert("Critical anomalies detected in backup metrics")
    
    return anomalies
```

### Backup Automático de Configuraciones

```python
# En DAG de configuraciones
@task
def backup_critical_configs():
    """Backup de configuraciones críticas."""
    config_backup = ConfigurationBackup()
    
    # Backup de variables de entorno de producción
    env_backup = config_backup.backup_environment_variables(
        env_prefix="PROD_",
        sensitive_keys=['PASSWORD', 'SECRET', 'KEY']
    )
    
    # Backup de archivos de configuración
    critical_files = [
        '/etc/app/production.yaml',
        '/etc/app/secrets.yaml',
        '/etc/nginx/nginx.conf'
    ]
    
    for config_file in critical_files:
        try:
            config_backup.backup_config_file(config_file)
        except Exception as e:
            logger.error(f"Failed to backup {config_file}: {e}")
    
    return {'status': 'completed'}
```

## Configuración

### Variables de Entorno

```bash
# Configuraciones
export CONFIG_BACKUP_DIR="/var/config-backups"
export CONFIG_ENV_PREFIX="PROD_"
export CONFIG_FILES_TO_BACKUP="/etc/app/config.yaml,/etc/app/secrets.yaml"

# ML (opcional)
# No requiere configuración adicional
```

## Beneficios

1. **Predicción Proactiva** - Detecta problemas antes de que ocurran
2. **Detección de Anomalías** - Identifica comportamiento inusual
3. **Backup de Configuraciones** - Protege configuraciones críticas
4. **Encriptación Automática** - Valores sensibles protegidos
5. **ML Inteligente** - Aprende de patrones históricos

## Dependencias ML (Opcionales)

```txt
numpy  # Cálculos numéricos
pandas  # Análisis de datos
scikit-learn  # Modelos de ML
```

Nota: El sistema funciona sin ML usando predicciones basadas en reglas.

## Próximos Pasos

1. Recopilar datos históricos para entrenar modelos
2. Configurar backups de configuraciones críticas
3. Integrar predicciones en DAGs de backup
4. Monitorear anomalías en tiempo real

¡Sistema de backups con ML y protección de configuraciones! 🚀

