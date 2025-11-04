# HashiCorp Vault - Gestión de Secretos

Este directorio contiene la configuración e integración de HashiCorp Vault para la gestión segura de secretos y credenciales en automatizaciones.

## Componentes

### 1. Instalación de Vault

**Ubicación**: `security/vault/values.yaml`

Vault se despliega mediante Helm en el namespace `security`:

```bash
# Instalación con Helmfile (recomendado)
helmfile apply

# O manualmente
helm install vault hashicorp/vault \
  --namespace security \
  --create-namespace \
  -f security/vault/values.yaml
```

**Configuración**:
- Alta disponibilidad (HA) con 3 réplicas
- Almacenamiento persistente (10Gi)
- UI habilitada
- CSI Driver para inyección de secretos en pods

### 2. Autenticación Kubernetes

Vault se configura para autenticar aplicaciones usando Service Accounts de Kubernetes.

**Script de configuración**: `security/vault/kubernetes-auth-config.sh`

```bash
# Ejecutar después de instalar Vault
export VAULT_ADDR=http://vault.security.svc.cluster.local:8200
export VAULT_TOKEN=<root-token>  # Obtener del init output
./security/vault/kubernetes-auth-config.sh
```

Este script:
- Habilita el auth method de Kubernetes
- Configura roles para diferentes servicios (Airflow, workflows, External Secrets)
- Aplica políticas de acceso

### 3. Políticas de Vault

**Ubicación**: `security/vault/vault-policies.hcl`

Las políticas definen qué secretos pueden leer cada servicio:

- **External Secrets Operator**: Acceso de lectura a todos los secretos para sincronización
- **Airflow workers**: Acceso a secretos de integraciones, BD, y notificaciones
- **Workflows**: Acceso a secretos de BPM, RPA, mensajería, y AI
- **Administradores**: Acceso completo (crear, leer, actualizar, eliminar)

### 4. Integración con External Secrets Operator

**Ubicación**: `security/vault/cluster-secret-store.yaml`

Configura Vault como backend para External Secrets Operator:

```bash
kubectl apply -f security/vault/cluster-secret-store.yaml
```

**Ejemplos de External Secrets**: `security/vault/external-secrets-examples.yaml`

Muestra cómo crear External Secrets que leen desde Vault:

```bash
kubectl apply -f security/vault/external-secrets-examples.yaml
```

### 5. Integración desde Python (Airflow)

**Módulo**: `data/airflow/plugins/vault_integration.py`

Proporciona funciones para acceder a secretos desde tareas de Airflow:

```python
from data.airflow.plugins.vault_integration import get_secret, VaultSecret

# Obtener un secreto
token = get_secret("crm/hubspot/token", "token")

# Usar como context manager
with VaultSecret("crm/hubspot/token", "token") as token:
    # usar token
    api_call(token)

# Obtener múltiples secretos
secrets = get_secrets_batch({
    "hubspot_token": "crm/hubspot/token",
    "db_url": "databases/leads/url"
})
```

**Autenticación**: Se usa automáticamente el Service Account del pod para autenticarse con Vault.

## Estructura de Secretos en Vault

Los secretos se organizan por categoría:

```
secret/data/
├── airflow/
│   ├── connections/
│   │   ├── snowflake
│   │   └── databricks
│   └── notifications/
├── crm/
│   └── hubspot/
│       └── token
├── databases/
│   └── leads/
│       ├── url
│       ├── username
│       └── password
├── bpm/
│   ├── flowable/
│   └── camunda/
├── rpa/
│   └── openrpa/
├── messaging/
│   └── whatsapp/
├── ai/
│   └── openai/
│       └── api_key
└── notifications/
    ├── slack/
    └── email/
```

## Inicialización de Vault

### Desarrollo

En desarrollo, Vault puede iniciarse en modo dev:

```bash
kubectl port-forward -n security svc/vault 8200:8200
export VAULT_ADDR=http://localhost:8200
vault operator init
```

### Producción

**PASO 1: Inicializar Vault**

```bash
vault operator init -key-shares=5 -key-threshold=3
```

Guardar los **unseal keys** y el **root token** de forma segura.

**PASO 2: Unseal Vault**

```bash
vault operator unseal <unseal-key-1>
vault operator unseal <unseal-key-2>
vault operator unseal <unseal-key-3>
```

**PASO 3: Configurar autenticación**

```bash
export VAULT_TOKEN=<root-token>
./security/vault/kubernetes-auth-config.sh
```

**PASO 4: Crear secretos**

```bash
# Ejemplo: Token de HubSpot
vault kv put secret/crm/hubspot/token token="your-hubspot-token"

# Ejemplo: Credenciales de BD
vault kv put secret/databases/leads/url url="jdbc:postgresql://..."
vault kv put secret/databases/leads/username username="dbuser"
vault kv put secret/databases/leads/password password="dbpass"
```

## Migración desde AWS Secrets Manager

Si ya tienes secretos en AWS Secrets Manager, puedes migrarlos a Vault:

1. **Listar secretos en AWS**:
```bash
aws secretsmanager list-secrets
```

2. **Leer y escribir en Vault**:
```bash
# Leer de AWS
SECRET=$(aws secretsmanager get-secret-value --secret-id crm/hubspot/token --query SecretString --output text)

# Escribir en Vault
vault kv put secret/crm/hubspot/token token="$SECRET"
```

O usar un script de migración automatizado (crear según necesidad).

## Seguridad

### Mejores Prácticas

1. **Rotación de secretos**: Implementar rotación automática usando Vault PKI o integraciones con proveedores externos
2. **Auditoría**: Habilitar audit logs en Vault para rastrear todos los accesos
3. **Politicas granulares**: Usar políticas específicas por servicio, no políticas amplias
4. **No almacenar en código**: Nunca hardcodear tokens o credenciales
5. **Autenticación de corta duración**: Los tokens tienen TTL limitado (1h-24h según el rol)

### Audit Logs

Habilitar audit logs:

```bash
vault audit enable file file_path=/vault/logs/audit.log
```

Los logs se pueden exportar a sistemas de SIEM para análisis de seguridad.

## Troubleshooting

### Vault no responde

```bash
# Verificar estado del pod
kubectl get pods -n security -l app.kubernetes.io/name=vault

# Ver logs
kubectl logs -n security -l app.kubernetes.io/name=vault

# Verificar si necesita unseal
kubectl exec -n security vault-0 -- vault status
```

### Error de autenticación

```bash
# Verificar que el Service Account tiene el token
kubectl get sa -n data airflow-worker

# Verificar políticas en Vault
vault policy read airflow-policy

# Probar autenticación manualmente
kubectl exec -n data <airflow-pod> -- \
  python -c "from data.airflow.plugins.vault_integration import get_vault_client; print(get_vault_client())"
```

### Secretos no se encuentran

```bash
# Listar secretos
vault kv list secret/

# Leer secreto directamente
vault kv get secret/crm/hubspot/token

# Verificar path en código
# Asegurarse de usar el path correcto: secret/data/... para KV v2
```

## Referencias

- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Vault Kubernetes Auth Method](https://www.vaultproject.io/docs/auth/kubernetes)
- [External Secrets Operator](https://external-secrets.io/)
- [Vault CSI Provider](https://developer.hashicorp.com/vault/docs/platform/k8s/csi)


