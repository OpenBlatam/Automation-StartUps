# Integración de Gmail Processor con el Stack

## Resumen

El DAG `gmail_processor` está completamente integrado con el stack de infraestructura:

- ✅ **External Secrets**: Credenciales gestionadas desde AWS Secrets Manager / Azure Key Vault
- ✅ **Variables de entorno**: Configuración en `values.yaml` de Airflow
- ✅ **Notificaciones Slack**: Integrado con el sistema de notificaciones existente
- ✅ **Logging estructurado**: Compatible con el stack de observabilidad

## Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────┐
│                    External Secrets Operator                │
│  (AWS Secrets Manager / Azure Key Vault / HashiCorp Vault)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Kubernetes Secret: gmail-secrets           │
│  - gmail-credentials-json                                   │
│  - gmail-token-json                                         │
│  - gmail-log-webhook-url                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Airflow values.yaml (Helm)                     │
│  Variables de entorno expuestas a workers:                   │
│  - GMAIL_CREDENTIALS_JSON                                   │
│  - GMAIL_TOKEN_JSON                                          │
│  - GMAIL_LOG_WEBHOOK_URL                                     │
│  - GMAIL_MAX_EMAILS                                          │
│  - GMAIL_LABEL_SIN_REVISAR                                   │
│  - GMAIL_LABEL_PROCESADO                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   DAG: gmail_processor                      │
│  - Lee variables de entorno (stack)                          │
│  - Parámetros opcionales sobreescriben valores               │
│  - Notificaciones Slack automáticas                         │
│  - Logging estructurado                                     │
└─────────────────────────────────────────────────────────────┘
```

## Archivos de Integración

### 1. External Secrets
- **Archivo**: `security/secrets/externalsecrets-gmail.yaml`
- **Secret**: `gmail-secrets` en namespace `data`
- **Soporta**: AWS Secrets Manager y Azure Key Vault

### 2. Configuración de Airflow
- **Archivo**: `data/airflow/values.yaml`
- **Sección**: `workers.env`
- **Variables**: GMAIL_* configuradas como secretKeyRef

### 3. DAG
- **Archivo**: `data/airflow/dags/gmail_processor.py`
- **Integración**: Lee desde `os.getenv()` con fallback a parámetros

### 4. Notificaciones
- **Plugin**: `data/airflow/plugins/etl_notifications.py`
- **Uso**: Notificaciones Slack automáticas al completar procesamiento

## Pasos de Despliegue

### 1. Configurar Secrets en Secrets Manager

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name integrations/gmail/credentials_json \
  --secret-string '{"installed":{"client_id":"...","client_secret":"..."}}'

aws secretsmanager create-secret \
  --name integrations/gmail/log_webhook_url \
  --secret-string "https://tu-servicio.com/api/logs"
```

**Azure Key Vault:**
```bash
az keyvault secret set \
  --vault-name myvault \
  --name integrations-gmail-credentials-json \
  --value '{"installed":{"client_id":"...","client_secret":"..."}}'
```

### 2. Aplicar External Secret

```bash
kubectl apply -f security/secrets/externalsecrets-gmail.yaml
```

### 3. Verificar Sincronización

```bash
# Ver ExternalSecret
kubectl get externalsecrets -n data

# Ver estado
kubectl describe externalsecret gmail-credentials -n data

# Ver Secret creado
kubectl get secret gmail-secrets -n data -o yaml
```

### 4. Actualizar Helm Chart (si es necesario)

Si usas Helm para desplegar Airflow, actualizar los valores:

```bash
helm upgrade airflow ./charts/airflow \
  -f data/airflow/values.yaml \
  -n data
```

### 5. Autorización Inicial de Gmail

La primera vez, el token OAuth2 debe generarse. Opciones:

**Opción A: Desarrollo Local**
- Ejecutar DAG localmente
- El flujo OAuth2 abrirá un navegador
- Guardar el token generado en Secrets Manager

**Opción B: Port Forward (Producción)**
```bash
kubectl port-forward -n data deployment/airflow-worker 8080:8080
# Ejecutar DAG y seguir el flujo OAuth2
```

**Opción C: Token Manual**
- Generar token fuera del cluster
- Guardarlo en Secrets Manager como `integrations/gmail/token_json`

### 6. Verificar DAG

```bash
# Ver DAG en Airflow UI
# O verificar logs
kubectl logs -n data deployment/airflow-scheduler | grep gmail_processor
```

## Monitoreo

### Notificaciones Slack

El DAG envía notificaciones automáticas a Slack cuando:
- ✅ Procesamiento completado exitosamente
- ⚠️ Procesamiento completado con errores
- ❌ Procesamiento falló completamente

Formato de notificación:
```
✅ Gmail Processor completado
• Procesados: 45
• Fallidos: 2
• Total: 47
• Modo: Producción
```

### Logs

Los logs se estructuran y pueden ser recolectados por:
- **Fluent Bit**: Logs de stdout/stderr
- **Loki**: Si está configurado
- **Elasticsearch**: Si está configurado

Formato de log:
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "dag_id": "gmail_processor",
  "message": "Gmail processing completed: 45 processed, 2 failed"
}
```

### Métricas (Futuro)

Se pueden agregar métricas de Prometheus:
- `gmail_emails_processed_total`
- `gmail_emails_failed_total`
- `gmail_processing_duration_seconds`

## Troubleshooting

### Error: "Secret gmail-secrets not found"

Verificar que External Secret está aplicado:
```bash
kubectl get externalsecrets -n data
kubectl describe externalsecret gmail-credentials -n data
```

### Error: "GMAIL_CREDENTIALS_JSON is required"

Verificar que las variables están en `values.yaml`:
```bash
kubectl get deployment airflow-worker -n data -o yaml | grep GMAIL
```

### Error: "Gmail API libraries not available"

Instalar dependencias en la imagen de Airflow:
```dockerfile
FROM apache/airflow:2.10.2-python3.11
RUN pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Seguridad

- ✅ Credenciales almacenadas en Secrets Manager (no en código)
- ✅ Tokens rotan automáticamente (OAuth2 refresh)
- ✅ Secrets no se exponen en logs
- ✅ Variables de entorno montadas como secretKeyRef
- ✅ External Secrets sincroniza cada hora (configurable)

## Próximas Mejoras

- [ ] Service Account para Gmail (evitar OAuth2 manual)
- [ ] Métricas de Prometheus
- [ ] Dashboard de Grafana
- [ ] Alertas en Prometheus Alertmanager
- [ ] Procesamiento en batch más eficiente
- [ ] Retry con backoff exponencial mejorado



