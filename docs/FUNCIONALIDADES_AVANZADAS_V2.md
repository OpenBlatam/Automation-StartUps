# 🚀 Funcionalidades Avanzadas V2 - Sistema de Backups

## Nuevas Características Implementadas

### 1. 🌐 API REST para Gestión (`backup_api.py`)

API completa para gestionar backups vía HTTP:

```python
from data.airflow.plugins.backup_api import create_backup_api

# Crear API
app = create_backup_api(
    backup_dir="/tmp/backups",
    encryption_key=encryption_key,
    api_key="your-secret-api-key"
)

# Ejecutar (ejemplo con gunicorn)
# gunicorn -w 4 -b 0.0.0.0:5000 backup_api:app
```

**Endpoints Disponibles:**

#### POST `/api/v1/backups`
Crear backup manualmente:
```json
{
  "type": "database",
  "connection_string": "postgresql://...",
  "db_type": "postgresql",
  "encrypt": true,
  "compress": true
}
```

#### GET `/api/v1/backups`
Listar backups:
```
GET /api/v1/backups?type=db&days=30
```

#### POST `/api/v1/backups/<backup_id>/restore`
Restaurar backup:
```json
{
  "connection_string": "postgresql://...",
  "db_type": "postgresql",
  "drop_existing": false
}
```

#### POST `/api/v1/backups/<backup_id>/verify`
Verificar backup:
```
POST /api/v1/backups/backup-123/verify
```

#### GET `/api/v1/metrics`
Obtener métricas:
```
GET /api/v1/metrics
```

#### GET `/api/v1/analytics/daily`
Obtener reporte diario:
```
GET /api/v1/analytics/daily?date=2025-01-15
```

#### GET `/api/v1/health`
Health check completo:
```
GET /api/v1/health
```

#### GET `/api/v1/predictions/space`
Predicción de espacio:
```
GET /api/v1/predictions/space?days=30
```

**Autenticación:**
- Header: `X-API-Key: your-secret-api-key`
- Configurar en variable de entorno: `BACKUP_API_KEY`

### 2. ☸️ Backups de Kubernetes (`backup_kubernetes.py`)

Backup automático de recursos de Kubernetes:

```python
from data.airflow.plugins.backup_kubernetes import KubernetesBackup

k8s_backup = KubernetesBackup()

# Backup de ConfigMaps
configmaps = k8s_backup.backup_configmaps(
    namespace=None,  # Todos los namespaces
    output_dir="/tmp/k8s-backups"
)

# Backup de Secrets (mantiene encriptación)
secrets = k8s_backup.backup_secrets(
    namespace="production",
    output_dir="/tmp/k8s-backups",
    decrypt=False  # Mantener encriptados
)

# Backup de Deployments
deployments = k8s_backup.backup_deployments(
    namespace=None,
    output_dir="/tmp/k8s-backups"
)

# Backup de todos los recursos
all_resources = k8s_backup.backup_all_resources(
    namespace=None,
    output_dir="/tmp/k8s-backups",
    resources=['configmaps', 'secrets', 'deployments']
)
```

**DAG Automático:**
- `k8s_backups`: Backups diarios de recursos de Kubernetes a las 3 AM
  - ConfigMaps
  - Secrets (encriptados)
  - Deployments
  - Comprime y encripta todo

### 3. 📊 Ejemplos de Uso de la API

#### Crear Backup desde Script

```bash
curl -X POST http://localhost:5000/api/v1/backups \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "database",
    "connection_string": "postgresql://user:pass@host:5432/db",
    "db_type": "postgresql",
    "encrypt": true,
    "compress": true
  }'
```

#### Restaurar Backup

```bash
curl -X POST http://localhost:5000/api/v1/backups/backup-123/restore \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "connection_string": "postgresql://user:pass@host:5432/db",
    "db_type": "postgresql",
    "drop_existing": false
  }'
```

#### Obtener Métricas

```bash
curl http://localhost:5000/api/v1/metrics \
  -H "X-API-Key: your-secret-api-key"
```

#### Verificar Backup

```bash
curl -X POST http://localhost:5000/api/v1/backups/backup-123/verify \
  -H "X-API-Key: your-secret-api-key"
```

### 4. 🔧 Configuración de la API

#### Variables de Entorno

```bash
export BACKUP_DIR="/var/backups"
export BACKUP_ENCRYPTION_KEY="..."
export BACKUP_API_KEY="your-secret-api-key"
export BACKUP_API_PORT=5000
```

#### Ejecutar API

```python
# En un script separado o como servicio
from data.airflow.plugins.backup_api import create_backup_api
from data.airflow.plugins.backup_encryption import BackupEncryption

encryption_key = BackupEncryption.load_key_from_env()

app = create_backup_api(
    backup_dir="/var/backups",
    encryption_key=encryption_key,
    api_key=os.getenv("BACKUP_API_KEY")
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

#### Con Gunicorn (Producción)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  backup_api:app
```

#### Con Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backup_api:app"]
```

### 5. 🎯 Casos de Uso Avanzados

#### Integración con CI/CD

```yaml
# .gitlab-ci.yml
backup_before_deploy:
  script:
    - |
      curl -X POST http://backup-api:5000/api/v1/backups \
        -H "X-API-Key: $BACKUP_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
          "type": "database",
          "connection_string": "$DB_CONNECTION",
          "db_type": "postgresql"
        }'
```

#### Dashboard de Monitoreo

```python
# Obtener métricas para dashboard
import requests

response = requests.get(
    "http://backup-api:5000/api/v1/metrics",
    headers={"X-API-Key": api_key}
)
metrics = response.json()

# Usar en dashboard
update_dashboard(metrics)
```

#### Webhook para Notificaciones

```python
# Integrar con webhooks externos
def backup_webhook(backup_id, status):
    payload = {
        'backup_id': backup_id,
        'status': status,
        'timestamp': datetime.now().isoformat()
    }
    
    requests.post(
        "https://your-webhook-url.com/backup",
        json=payload
    )
```

### 6. 🔒 Seguridad de la API

#### Autenticación

- API Key requerida en header `X-API-Key`
- Configurar en variable de entorno
- Rotar periódicamente

#### HTTPS

En producción, usar HTTPS:
```bash
# Con certificado SSL
gunicorn --certfile=cert.pem --keyfile=key.pem \
  -b 0.0.0.0:5000 backup_api:app
```

#### Rate Limiting

Agregar rate limiting (ejemplo con Flask-Limiter):
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 7. 📈 Métricas de la API

#### Endpoints de Métricas

- `GET /api/v1/metrics` - Métricas de backups
- `GET /api/v1/health` - Health check completo
- `GET /api/v1/predictions/space` - Predicciones

#### Integración con Prometheus

```python
from prometheus_client import Counter, Histogram

api_requests = Counter('backup_api_requests_total', 'Total API requests')
api_duration = Histogram('backup_api_duration_seconds', 'API request duration')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    api_requests.inc()
    if hasattr(request, 'start_time'):
        api_duration.observe(time.time() - request.start_time)
    return response
```

## Resumen de Nuevas Funcionalidades

1. ✅ **API REST Completa** - Gestión vía HTTP
2. ✅ **Backups de Kubernetes** - ConfigMaps, Secrets, Deployments
3. ✅ **DAG de K8s Backups** - Automatización completa
4. ✅ **Autenticación API** - API Key based
5. ✅ **Documentación Completa** - Ejemplos y casos de uso

## Dependencias Nuevas

```txt
flask  # API REST
kubernetes  # Cliente de Kubernetes
pyyaml  # Manejo de YAML
```

## Próximos Pasos

1. Configurar API Key
2. Desplegar API (gunicorn/Docker)
3. Configurar backups de Kubernetes
4. Integrar con sistemas externos
5. Monitorear con Prometheus

¡Sistema completo de backups con API REST y soporte Kubernetes! 🚀

