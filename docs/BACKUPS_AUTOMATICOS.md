# Sistema de Backups Automáticos

Sistema completo de backups automáticos con encriptación, sincronización en la nube y alertas de seguridad.

## 🎯 Características

- ✅ **Backups Automáticos**: Bases de datos, archivos y configuraciones
- ✅ **Encriptación**: AES-256 para proteger datos sensibles
- ✅ **Sincronización en Nube**: AWS S3, Azure Blob Storage, GCP Cloud Storage
- ✅ **Alertas de Seguridad**: Notificaciones automáticas de fallos y problemas
- ✅ **Verificación de Integridad**: Checksums SHA-256
- ✅ **Limpieza Automática**: Retención configurable de backups antiguos
- ✅ **Sin Intervención Manual**: Todo funciona automáticamente

## 📦 Componentes

### 1. Módulos Python

- **`backup_manager.py`**: Gestor principal de backups
  - `DatabaseBackup`: Backups de PostgreSQL/MySQL
  - `FileBackup`: Backups de archivos y directorios
  - `CloudSync`: Sincronización con servicios de nube
  - `BackupManager`: Orquestador principal

- **`backup_encryption.py`**: Módulo de encriptación
  - `BackupEncryption`: Encriptación simétrica (AES-256)
  - `SensitiveDataEncryption`: Encriptación de datos sensibles (PII)

- **`backup_notifications.py`**: Sistema de alertas
  - `BackupNotifier`: Notificaciones de backups
  - `SecurityAlertManager`: Alertas de seguridad

### 2. DAGs de Airflow

- **`automated_backups.py`**: Backups diarios completos
  - Backup de bases de datos
  - Backup de archivos críticos
  - Limpieza automática
  - Verificación de integridad

- **`incremental_backups.py`**: Backups incrementales (cada 6 horas)

- **`security_monitoring.py`**: Monitoreo continuo de seguridad
  - Detección de intentos de acceso no autorizados
  - Verificación de estado de backups
  - Verificación de encriptación
  - Verificación de sincronización en nube

## 🚀 Instalación

### 1. Ejecutar Script de Configuración

```bash
cd scripts
chmod +x setup_automated_backups.sh
./setup_automated_backups.sh
```

El script:
- Genera clave de encriptación
- Crea archivo de variables de entorno
- Crea directorio de backups
- Instala dependencias Python

### 2. Configurar Variables de Entorno

Edita `.env.backups` generado:

```bash
# Directorio de backups
export BACKUP_DIR="/var/backups"

# Clave de encriptación (generada automáticamente)
export BACKUP_ENCRYPTION_KEY="tu_clave_base64"

# Proveedor de nube
export CLOUD_PROVIDER="aws"  # aws, azure, gcp

# AWS S3
export AWS_BACKUP_BUCKET="mi-bucket-backups"
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
export AWS_REGION="us-east-1"

# Bases de datos
export BACKUP_DB_CONNECTIONS="postgresql://user:pass@host:5432/db1,postgresql://user:pass@host:5432/db2"

# Archivos críticos
export BACKUP_CRITICAL_PATHS="/etc,/opt/config,/var/app/data"

# Notificaciones
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export BACKUP_ALERT_EMAILS="admin@example.com,ops@example.com"
```

### 3. Cargar Variables en Airflow

Agrega las variables al archivo de entorno de Airflow o en la UI de Airflow:

```bash
# En docker-compose.yml o Kubernetes
environment:
  - BACKUP_ENCRYPTION_KEY=${BACKUP_ENCRYPTION_KEY}
  - AWS_BACKUP_BUCKET=${AWS_BACKUP_BUCKET}
  # ... etc
```

## 📋 Uso

### Backups Manuales

```python
from data.airflow.plugins.backup_manager import BackupManager, BackupConfig
from data.airflow.plugins.backup_encryption import BackupEncryption

# Cargar clave de encriptación
encryption_key = BackupEncryption.load_key_from_env()

# Crear gestor
manager = BackupManager(
    backup_dir="/tmp/backups",
    encryption_key=encryption_key,
    cloud_config={
        "provider": "aws",
        "config": {
            "bucket": "mi-bucket",
            "access_key_id": "...",
            "secret_access_key": "...",
            "region": "us-east-1"
        }
    }
)

# Backup de base de datos
result = manager.backup_database(
    connection_string="postgresql://user:pass@host:5432/db",
    db_type="postgresql",
    config=BackupConfig(
        encrypt=True,
        compress=True,
        cloud_sync=True,
        retention_days=30
    )
)

# Backup de archivos
result = manager.backup_files(
    source_paths=["/etc", "/opt/config"],
    config=BackupConfig(encrypt=True, cloud_sync=True)
)
```

### Encriptación de Datos Sensibles

```python
from data.airflow.plugins.backup_encryption import SensitiveDataEncryption

encryption = SensitiveDataEncryption(encryption_key)

# Encriptar campo sensible
data = {
    "email": "user@example.com",
    "phone": "1234567890",
    "ssn": "123-45-6789"
}

encrypted = encryption.encrypt_dict(
    data,
    sensitive_fields=["email", "phone", "ssn"]
)

# Desencriptar
decrypted = encryption.decrypt_dict(
    encrypted,
    sensitive_fields=["email", "phone", "ssn"]
)
```

### Alertas de Seguridad

```python
from data.airflow.plugins.backup_notifications import SecurityAlertManager, AlertLevel

security_manager = SecurityAlertManager()

# Alerta de fallo de backup
security_manager.alert_backup_failure(
    backup_id="backup-123",
    error="Connection timeout",
    details={"database": "prod_db"}
)

# Alerta de acceso no autorizado
security_manager.alert_unauthorized_access(
    resource="database",
    user="suspicious_user",
    ip="192.168.1.100"
)
```

## 🔒 Seguridad

### Encriptación

- **Algoritmo**: AES-256 (Fernet)
- **Derivación de Clave**: PBKDF2 con 100,000 iteraciones
- **Salt**: Generado aleatoriamente

### Almacenamiento de Claves

**⚠️ IMPORTANTE**: La clave de encriptación debe almacenarse de forma segura:

1. **Variables de Entorno**: Usar secretos de Kubernetes/Secrets Manager
2. **HashiCorp Vault**: Almacenar en Vault
3. **AWS Secrets Manager**: Usar Secrets Manager
4. **Azure Key Vault**: Usar Key Vault

**NUNCA**:
- ❌ Commitear la clave en Git
- ❌ Hardcodear en el código
- ❌ Almacenar en texto plano

### Mejores Prácticas

1. **Rotación de Claves**: Rotar claves periódicamente
2. **Backup de Claves**: Guardar clave en lugar seguro y separado
3. **Permisos**: Restringir acceso a directorio de backups
4. **Monitoreo**: Revisar alertas regularmente
5. **Pruebas de Restauración**: Probar restauraciones periódicamente

## ☁️ Proveedores de Nube

### AWS S3

```yaml
cloud_config:
  provider: aws
  config:
    bucket: "mi-bucket-backups"
    access_key_id: "AKIA..."
    secret_access_key: "secret"
    region: "us-east-1"
```

**Requisitos IAM**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::mi-bucket-backups",
        "arn:aws:s3:::mi-bucket-backups/*"
      ]
    }
  ]
}
```

### Azure Blob Storage

```yaml
cloud_config:
  provider: azure
  config:
    connection_string: "DefaultEndpointsProtocol=https;AccountName=..."
    container: "backups"
```

### GCP Cloud Storage

```yaml
cloud_config:
  provider: gcp
  config:
    bucket: "mi-bucket-backups"
    credentials_path: "/path/to/service-account.json"
```

## 📊 Monitoreo

### Métricas

El sistema genera métricas automáticamente:

- Tamaño de backups
- Duración de backups
- Tasa de éxito/fallo
- Backups en nube vs local
- Alertas de seguridad

### Dashboard

Ver estado en Airflow UI:
- DAG: `automated_backups`
- DAG: `security_monitoring`

### Logs

Los logs se almacenan en:
- Airflow logs (normal)
- Archivo de historial de alertas (en memoria)

## 🔧 Troubleshooting

### Backup Fallido

1. Verificar logs de Airflow
2. Verificar conectividad a base de datos
3. Verificar espacio en disco
4. Verificar permisos de directorio

### Error de Encriptación

1. Verificar que `BACKUP_ENCRYPTION_KEY` esté configurado
2. Verificar formato (debe ser base64)
3. Verificar permisos de archivo

### Error de Sincronización en Nube

1. Verificar credenciales
2. Verificar conectividad de red
3. Verificar permisos del bucket/container
4. Verificar región/configuración

### Restaurar Backup

```python
from data.airflow.plugins.backup_manager import BackupManager
from data.airflow.plugins.backup_encryption import BackupEncryption

# Cargar clave
encryption_key = BackupEncryption.load_key_from_env()

# Desencriptar backup
encryption = BackupEncryption(encryption_key)
encryption.decrypt_file(
    "backup.sql.gz.encrypted",
    "backup.sql.gz"
)

# Descomprimir
import gzip
with gzip.open("backup.sql.gz", "rb") as f_in:
    with open("backup.sql", "wb") as f_out:
        f_out.write(f_in.read())

# Restaurar base de datos
# psql -h host -U user -d database < backup.sql
```

## 📅 Programación

### Backups Completos

- **Frecuencia**: Diario (2 AM UTC)
- **Duración**: ~1-2 horas
- **Retención**: 30 días (configurable)

### Backups Incrementales

- **Frecuencia**: Cada 6 horas
- **Duración**: ~15-30 minutos
- **Retención**: 7 días

### Monitoreo de Seguridad

- **Frecuencia**: Cada 15 minutos
- **Duración**: ~5-10 minutos

## 🎛️ Configuración Avanzada

### Retención Personalizada

```python
# En el DAG, usar parámetros
params = {
    'retention_days': 90,  # 90 días
    'backup_type': 'full',
    'encrypt': True,
    'cloud_sync': True
}
```

### Excluir Archivos

```python
file_backup = FileBackup()
result = file_backup.create_backup(
    source_paths=["/var/app"],
    output_path="backup.tar.gz",
    exclude_patterns=["*.log", "*.tmp", "__pycache__"]
)
```

### Backup Selectivo de Tablas

```python
db_backup = DatabaseBackup(connection_string, "postgresql")
result = db_backup.create_backup(
    output_path="backup.sql",
    tables=["users", "orders", "payments"],
    schema_only=False
)
```

## 📚 Referencias

- [Documentación de Cryptography](https://cryptography.io/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Azure Blob Storage](https://docs.microsoft.com/azure/storage/blobs/)
- [GCP Cloud Storage](https://cloud.google.com/storage/docs)

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar logs de Airflow
2. Verificar configuración de variables de entorno
3. Revisar documentación de proveedor de nube
4. Contactar al equipo de plataforma

