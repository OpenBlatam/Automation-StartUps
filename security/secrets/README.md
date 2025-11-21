# External Secrets - Gestión de Secretos

Esta carpeta contiene las configuraciones de External Secrets Operator (ESO) para sincronizar secretos desde proveedores externos (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault) a Kubernetes Secrets.

## Descripción

External Secrets Operator sincroniza secretos de proveedores externos a Kubernetes, eliminando la necesidad de manejar secretos manualmente y mejorando la seguridad.

## Estructura

```
secrets/
├── externalsecrets-aws.yaml           # Configuración para AWS Secrets Manager
├── externalsecrets-azure.yaml        # Configuración para Azure Key Vault
├── externalsecrets-airflow-notify.yaml # Secretos de notificaciones para Airflow
├── externalsecrets-hubspot-db.yaml   # HubSpot y DB para workflows
├── externalsecrets-stripe-sheets-openai-db.yaml # Stripe, Sheets, OpenAI, DB
├── externalsecrets-stripe-quickbooks.yaml # Stripe + QuickBooks para Airflow
├── externalsecrets-flowable-openrpa.yaml # Flowable y OpenRPA
└── externalsecrets-whatsapp-ocr.yaml # WhatsApp y OCR (OpenAI)
```

## Componentes

### ClusterSecretStore

Define la conexión al proveedor de secretos (AWS, Azure, Vault).

### ExternalSecret

Define qué secretos sincronizar y a qué Kubernetes Secret.

## Configuración por Proveedor

### AWS Secrets Manager

**Archivo**: `externalsecrets-aws.yaml`

**Requisitos**:
- IRSA (IAM Roles for Service Accounts) configurado
- IAM Role con permisos para Secrets Manager

**Aplicar**:

```bash
kubectl apply -f security/secrets/externalsecrets-aws.yaml
```

**Ejemplo**:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: externalsecrets-sa
            namespace: security
```

### Azure Key Vault

**Archivo**: `externalsecrets-azure.yaml`

**Requisitos**:
- Workload Identity configurado
- Service Principal con permisos en Key Vault

**Aplicar**:

```bash
kubectl apply -f security/secrets/externalsecrets-azure.yaml
```

### HashiCorp Vault

Ver `security/vault/README.md` para configuración completa.

## Secretos por Aplicación

### Airflow - Notificaciones

**Archivo**: `externalsecrets-airflow-notify.yaml`

**Secretos sincronizados**:
- `slack-webhook-url`: URL de webhook de Slack
- `alert-emails`: Lista de emails para alertas

**Uso**:

```python
# En DAGs de Airflow
from airflow.models import Variable
slack_webhook = Variable.get("slack_webhook_url")
```

### Workflows - HubSpot + DB + ManyChat

**Archivo**: `externalsecrets-hubspot-db.yaml`

**Secretos sincronizados**:
- `hubspot_token`: Token de API de HubSpot
- `manychat_api_key`: API Key de ManyChat para envío de mensajes
- `jdbc_url`, `jdbc_user`, `jdbc_password`: Conexión a base de datos

**Uso en Kestra**:

```yaml
# Variables se mapean desde ExternalSecret
inputs:
  - name: hubspot_token
    type: STRING
    value: "{{ vars.hubspot_token }}"
  - name: manychat_api_key
    type: STRING
    value: "{{ vars.manychat_api_key }}"
```

**Crear secrets en AWS Secrets Manager**:

```bash
# ManyChat API Key
aws secretsmanager create-secret \
  --name messaging/manychat/api_key \
  --secret-string "YOUR_MANYCHAT_API_KEY"

# HubSpot Token (si no existe)
aws secretsmanager create-secret \
  --name crm/hubspot/token \
  --secret-string "YOUR_HUBSPOT_TOKEN"
```

### Stripe + Sheets + OpenAI + DB

**Archivo**: `externalsecrets-stripe-sheets-openai-db.yaml`

**Secretos sincronizados**:
- `stripe_api_key`: API key de Stripe
- `stripe_signing_secret`: Secret para validar webhooks
- `sheets_credentials`: Credenciales de Google Sheets
- `openai_api_key`: API key de OpenAI
- `db_*`: Credenciales de base de datos

### Stripe + QuickBooks (Airflow)

**Archivo**: `externalsecrets-stripe-quickbooks.yaml`

**Namespace**: `data` (para Airflow DAGs)

**Secretos sincronizados**:
- `STRIPE_API_KEY`: API key de Stripe para obtener pagos y tarifas
- `QUICKBOOKS_ACCESS_TOKEN`: Access token OAuth2 de QuickBooks Online
- `QUICKBOOKS_REALM_ID`: Company ID (Realm ID) de QuickBooks

**Uso en Airflow DAGs**:
```python
# El DAG stripe_fees_to_quickbooks.py usa estas variables automáticamente
import os
stripe_key = os.environ.get("STRIPE_API_KEY")
qb_token = os.environ.get("QUICKBOOKS_ACCESS_TOKEN")
qb_realm = os.environ.get("QUICKBOOKS_REALM_ID")
```

**Configurar secretos en AWS Secrets Manager**:
```bash
# Stripe API Key
aws secretsmanager create-secret \
  --name payments/stripe/api_key \
  --secret-string "sk_live_..."

# QuickBooks Access Token
aws secretsmanager create-secret \
  --name accounting/quickbooks/access_token \
  --secret-string "eyJraWQiOi..."

# QuickBooks Realm ID
aws secretsmanager create-secret \
  --name accounting/quickbooks/realm_id \
  --secret-string "1234567890"
```

### Flowable + OpenRPA

**Archivo**: `externalsecrets-flowable-openrpa.yaml`

**Secretos sincronizados**:
- `flowable_token`: Token de autenticación Flowable
- `openrpa_webhook_url`: URL de webhook de OpenRPA

### WhatsApp + OCR

**Archivo**: `externalsecrets-whatsapp-ocr.yaml`

**Secretos sincronizados**:
- `whatsapp_token`: Token de WhatsApp Business API
- `openai_api_key`: Para OCR de imágenes
- `sheets_credentials`: Para guardar resultados
- `docs_credentials`: Para generar documentos

### HubSpot + ManyChat Integration

**Archivo**: `externalsecrets-manychat.yaml`

**Secretos sincronizados**:
- `manychat_api_key`: API Key de ManyChat para autenticación
- `manychat_page_id`: ID de la página de ManyChat (opcional)
- `hubspot_webhook_secret`: Secret para verificar webhooks de HubSpot (opcional)

**Uso en Kestra**:
```yaml
inputs:
  - name: manychat_api_key
    type: STRING
    value: "{{ vars.manychat_api_key }}"
  - name: hubspot_token
    type: STRING
    value: "{{ vars.hubspot_token }}"
  - name: hubspot_webhook_secret
    type: STRING
    value: "{{ vars.hubspot_webhook_secret }}"
```

**Nota**: Los secretos de HubSpot están en `externalsecrets-hubspot-db.yaml`

### Gmail Processor

**Archivo**: `externalsecrets-gmail.yaml`

**Secretos sincronizados**:
- `gmail-credentials-json`: Credenciales OAuth2 de Gmail (JSON string)
- `gmail-token-json`: Token OAuth2 almacenado (JSON string, se genera en primera ejecución)
- `gmail-log-webhook-url`: URL del webhook para enviar logs de correos procesados

**Namespace**: `data` (para Airflow)

**Uso en Airflow**:
- Las credenciales se exponen como variables de entorno
- Ver `data/airflow/values.yaml` para configuración completa
- El DAG `gmail_processor` lee desde `GMAIL_CREDENTIALS_JSON`, `GMAIL_TOKEN_JSON`, etc.

## Uso

### Verificar sincronización

```bash
# Ver ExternalSecrets
kubectl get externalsecrets -A

# Ver estado de sincronización
kubectl describe externalsecret <name> -n <namespace>

# Ver Kubernetes Secrets creados
kubectl get secrets -n <namespace>

# Ver contenido (decodificar base64)
kubectl get secret <secret-name> -n <namespace> -o jsonpath='{.data.key}' | base64 -d
```

### Forzar resincronización

```bash
# Eliminar y recrear ExternalSecret
kubectl delete externalsecret <name> -n <namespace>
kubectl apply -f security/secrets/externalsecrets-<name>.yaml

# O anotar para refresh inmediato
kubectl annotate externalsecret <name> -n <namespace> \
  force-sync=$(date +%s) --overwrite
```

### Ver logs

```bash
# Logs del operador
kubectl logs -n external-secrets-system deployment/external-secrets -f

# Logs de sincronización específica
kubectl logs -n external-secrets-system deployment/external-secrets | \
  grep "<secret-name>"
```

## Crear Nuevo ExternalSecret

### 1. Crear secret en proveedor externo

**AWS**:

```bash
aws secretsmanager create-secret \
  --name myapp/database/password \
  --secret-string "my-secret-password"
```

**Azure**:

```bash
az keyvault secret set \
  --vault-name my-keyvault \
  --name myapp-database-password \
  --value "my-secret-password"
```

### 2. Crear ExternalSecret

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-db-credentials
  namespace: myapp
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager  # O azure-keyvault, vault
    kind: ClusterSecretStore
  target:
    name: myapp-db-credentials
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: myapp/database/password
    - secretKey: username
      remoteRef:
        key: myapp/database/username
```

### 3. Aplicar

```bash
kubectl apply -f my-externalsecret.yaml

# Verificar
kubectl get externalsecret myapp-db-credentials -n myapp
kubectl get secret myapp-db-credentials -n myapp
```

## Monitoreo

### Métricas de Prometheus

External Secrets expone métricas:

```bash
# Ver métricas
kubectl port-forward -n external-secrets-system \
  service/external-secrets-metrics 8080:8080
curl http://localhost:8080/metrics

# Métricas clave:
# - external_secrets_operator_reconcile_duration_seconds
# - external_secrets_operator_sync_calls_total
# - external_secrets_operator_secrets_total
```

### ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: external-secrets
  namespace: external-secrets-system
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: external-secrets
  endpoints:
    - port: http-metrics
      interval: 30s
```

## Seguridad

### IAM/Service Principals

- **Principio de menor privilegio**: Solo permisos necesarios para leer secretos
- **Rotación**: Rotar secretos cada 90 días
- **Auditoría**: Habilitar CloudTrail/Azure Monitor para tracking

### Secrets en Rest

- Los Kubernetes Secrets se almacenan en etcd (pueden estar encriptados)
- Considerar usar KMS provider para encriptación en etcd

### Secrets in Transit

- TLS para comunicación con proveedores externos
- Validar certificados

## Troubleshooting

### Secret no se sincroniza

```bash
# Ver estado del ExternalSecret
kubectl describe externalsecret <name> -n <namespace>

# Ver condiciones
kubectl get externalsecret <name> -n <namespace> -o yaml | \
  grep -A 10 conditions

# Verificar permisos
# AWS: Verificar IRSA role
kubectl describe serviceaccount externalsecrets-sa -n security

# Azure: Verificar Workload Identity
kubectl get serviceaccount <sa> -o yaml | grep azure.workload.identity
```

### Error de autenticación

```bash
# Ver logs detallados
kubectl logs -n external-secrets-system deployment/external-secrets | \
  grep -i auth

# Verificar credenciales del proveedor
# AWS: Verificar IAM role
# Azure: Verificar Service Principal
```

### Secret sincronizado pero no accesible

```bash
# Verificar que el Secret existe
kubectl get secret <name> -n <namespace>

# Verificar que el pod tiene permisos para leer el Secret
kubectl get serviceaccount -n <namespace>
kubectl get rolebinding,clusterrolebinding -n <namespace>
```

## Mejores Prácticas

1. **Usar ClusterSecretStore compartido**: Para múltiples namespaces
2. **Refresh interval apropiado**: Balance entre actualización y carga (1h recomendado)
3. **Rotar secretos regularmente**: Automatizar rotación cada 90 días
4. **No hardcodear secretos**: Siempre usar External Secrets
5. **Separar por aplicación**: Un ExternalSecret por aplicación
6. **Usar secret keys descriptivos**: Nombres claros para las claves
7. **Monitorear sincronizaciones**: Alertar en fallos de sincronización

## Referencias

- [External Secrets Operator Documentation](https://external-secrets.io/)
- [AWS Secrets Manager Integration](https://external-secrets.io/v0.9.0/provider/aws-secrets-manager/)
- [Azure Key Vault Integration](https://external-secrets.io/v0.9.0/provider/azure-key-vault/)
- [Vault Integration](https://external-secrets.io/v0.9.0/provider/hashicorp-vault/)

