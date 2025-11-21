# Guía de Deployment del Sistema de Contratos

## 📋 Checklist de Deployment

### 1. Pre-requisitos

- [ ] PostgreSQL 12+ con permisos de creación de tablas
- [ ] Apache Airflow 2.5+
- [ ] Python 3.8+
- [ ] Acceso a DocuSign o PandaDoc (opcional)
- [ ] Slack webhook URL (opcional, para notificaciones)
- [ ] AWS S3 o Google Cloud Storage (opcional, para almacenamiento)

### 2. Instalación de Dependencias

```bash
# Instalar dependencias base
pip install apache-airflow[postgres]==2.5.0
pip install requests
pip install cryptography  # Para DocuSign JWT

# Dependencias opcionales
pip install boto3  # Para S3
pip install google-cloud-storage  # Para GCS
pip install flask  # Para API REST y webhooks
```

### 3. Configuración de Base de Datos

```bash
# Ejecutar schema
psql -U postgres -d your_database -f data/db/contract_management_schema.sql

# Verificar tablas creadas
psql -U postgres -d your_database -c "\dt contract*"
```

### 4. Variables de Entorno

Crear archivo `.env` o configurar en Airflow:

```bash
# PostgreSQL
export AIRFLOW_CONN_POSTGRES_DEFAULT="postgresql://user:pass@host:5432/dbname"

# DocuSign
export DOCUSIGN_API_BASE_URL="https://demo.docusign.net"  # o https://www.docusign.net para prod
export DOCUSIGN_ACCOUNT_ID="your_account_id"
export DOCUSIGN_INTEGRATION_KEY="your_integration_key"
export DOCUSIGN_USER_ID="your_user_id"
export DOCUSIGN_PRIVATE_KEY_PATH="/path/to/private_key.pem"
export DOCUSIGN_WEBHOOK_SECRET="your_webhook_secret"  # Para webhooks

# PandaDoc
export PANDADOC_API_KEY="your_api_key"
export PANDADOC_API_BASE_URL="https://api.pandadoc.com"

# Notificaciones
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Almacenamiento (opcional)
export CONTRACT_STORAGE_TYPE="s3"  # o "gcs" o "local"
export S3_CONTRACTS_BUCKET="your-bucket-name"
export AWS_REGION="us-east-1"
export GCS_CONTRACTS_BUCKET="your-bucket-name"

# Rate Limiting (opcional)
export CONTRACT_RATE_LIMIT_API="1000"  # requests/hora
export CONTRACT_RATE_LIMIT_CREATE="100"  # requests/hora
export CONTRACT_RATE_LIMIT_SEND="50"  # requests/hora
```

### 5. Configuración de Airflow Connections

```python
# En Airflow UI o CLI
from airflow.models import Connection
from airflow import settings

# PostgreSQL
conn = Connection(
    conn_id='postgres_default',
    conn_type='postgres',
    host='localhost',
    login='postgres',
    password='password',
    schema='your_database',
    port=5432
)
session = settings.Session()
session.add(conn)
session.commit()
```

### 6. Crear Plantillas de Contratos

```sql
-- Ejemplo de plantilla de contrato laboral
INSERT INTO contract_templates (
    template_id, name, description, contract_type, template_content,
    template_variables, default_expiration_days, default_reminder_days,
    requires_legal_review, requires_manager_approval, signers_required,
    is_active, created_by
) VALUES (
    'employment_contract_v1',
    'Contrato Laboral Estándar',
    'Contrato laboral con cláusulas estándar',
    'employment',
    'CONTRATO LABORAL

Entre {{company_name}}, representada por {{company_representative}}, y {{employee_name}},
identificado con DNI {{employee_dni}}, se establece el siguiente contrato:

1. POSICIÓN: {{position}}
2. SALARIO: {{salary}}
3. FECHA DE INICIO: {{start_date}}
4. DURACIÓN: {{duration}} días

Firma del Empleado: _______________
Firma del Representante: _______________',
    '{"company_name": "string", "company_representative": "string", "employee_name": "string", "employee_dni": "string", "position": "string", "salary": "string", "start_date": "date", "duration": "integer"}'::jsonb,
    365,
    ARRAY[90, 60, 30, 14, 7],
    false,
    true,
    '[{"role": "employee", "order": 1}, {"role": "manager", "order": 2}]'::jsonb,
    true,
    'admin@example.com'
);
```

### 7. Verificar DAGs

```bash
# Listar DAGs
airflow dags list | grep contract

# Verificar sintaxis
airflow dags list-import-errors

# Probar un DAG
airflow dags test contract_management 2024-01-01
```

### 8. Activar DAGs

En Airflow UI:
1. Ir a DAGs
2. Activar los siguientes DAGs:
   - `contract_renewal_reminders` (diario)
   - `contract_status_monitor` (cada 6h)
   - `contract_auto_renewal` (diario)
   - `contract_reports` (semanal)
   - `contract_reconciliation` (cada 12h)
   - `contract_gdpr_cleanup` (mensual)
   - `contract_ml_insights` (diario)

### 9. Configurar Webhooks (Opcional)

#### DocuSign Connect
1. Ir a DocuSign Admin > Connect
2. Crear nueva configuración
3. URL: `https://your-domain.com/webhooks/docusign`
4. Eventos: `envelope-completed`, `envelope-signed`, `envelope-declined`
5. Guardar secret key en `DOCUSIGN_WEBHOOK_SECRET`

#### PandaDoc Webhooks
1. Ir a Settings > Webhooks
2. Agregar endpoint: `https://your-domain.com/webhooks/pandadoc`
3. Eventos: `document_completed`, `document_deleted`

#### Desplegar Servidor de Webhooks

```python
# webhook_server.py
from data.airflow.plugins.contract_webhooks import create_webhook_app

app = create_webhook_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 10. Desplegar API REST (Opcional)

```python
# api_server.py
from data.airflow.plugins.contract_api import create_contract_api

app = create_contract_api(api_key="your-secure-api-key")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
```

O usar Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8080 api_server:app
```

### 11. Configurar Monitoreo

```bash
# Verificar métricas
airflow dags test contract_reports 2024-01-01

# Verificar logs
tail -f /path/to/airflow/logs/contract_*/task_instance.log
```

### 12. Testing

```bash
# Test de creación de contrato
python -c "
from data.airflow.plugins.contract_integrations import create_contract_from_template
result = create_contract_from_template(
    template_id='employment_contract_v1',
    primary_party_email='test@example.com',
    primary_party_name='Test User',
    contract_variables={'employee_name': 'Test User', 'position': 'Engineer'}
)
print(result)
"
```

## 🔧 Troubleshooting

### Error: "Plantilla no encontrada"
- Verificar que la plantilla existe en BD
- Verificar que `is_active = true`

### Error: "DocuSign access token no disponible"
- Verificar variables de entorno
- Verificar que la clave privada existe y es válida
- Verificar permisos de la aplicación en DocuSign

### Error: "Rate limit exceeded"
- Ajustar límites en `contract_rate_limiter.py`
- Verificar que no hay múltiples procesos haciendo requests

### Error: "Circuit breaker is OPEN"
- El servicio externo está caído
- Esperar timeout o resetear manualmente
- Verificar logs del proveedor

## 📊 Verificación Post-Deployment

1. ✅ Crear un contrato de prueba
2. ✅ Verificar que se envía para firma
3. ✅ Verificar que se actualiza el estado
4. ✅ Verificar notificaciones Slack
5. ✅ Verificar que se almacena versión firmada
6. ✅ Verificar reportes semanales
7. ✅ Verificar reconciliación automática

## 🚀 Producción

### Recomendaciones
- Usar conexión pooling para PostgreSQL
- Configurar backups automáticos de BD
- Monitorear logs y métricas
- Configurar alertas para errores críticos
- Revisar rate limits según carga esperada
- Configurar auto-scaling para API REST
- Usar HTTPS para webhooks y API
- Rotar API keys regularmente

### Escalabilidad
- El sistema está diseñado para manejar miles de contratos
- Usar caché de plantillas (ya implementado)
- Considerar Redis para rate limiting distribuido
- Usar almacenamiento cloud para documentos
- Considerar sharding de BD si es necesario

---

**Sistema listo para deployment** ✅

