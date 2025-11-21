# 🔒 Guía de Seguridad

> **Versión**: 1.0 | **Última actualización**: 2024

Guía completa de seguridad para la plataforma.

## 📋 Tabla de Contenidos

- [Principios de Seguridad](#-principios-de-seguridad)
- [Gestión de Secretos](#-gestión-de-secretos)
- [Autenticación y Autorización](#-autenticación-y-autorización)
- [Seguridad de Red](#-seguridad-de-red)
- [Seguridad de Datos](#-seguridad-de-datos)
- [Auditoría y Compliance](#-auditoría-y-compliance)
- [Mejores Prácticas](#-mejores-prácticas)
- [Checklist de Seguridad](#-checklist-de-seguridad)

---

## 🛡️ Principios de Seguridad

### Defense in Depth

Múltiples capas de seguridad:
1. **Network Layer**: Network Policies, firewalls
2. **Application Layer**: RBAC, autenticación
3. **Data Layer**: Encryption at rest y in transit
4. **Secret Management**: Vault, External Secrets

### Least Privilege

- Usuarios y servicios solo tienen los permisos mínimos necesarios
- Revisar y actualizar permisos regularmente
- Usar service accounts específicos por aplicación

### Zero Trust

- No confiar en ninguna conexión por defecto
- Verificar cada solicitud
- Autenticar y autorizar todo

---

## 🔐 Gestión de Secretos

### Vault

**HashiCorp Vault** para gestión centralizada de secretos:

```bash
# Verificar que Vault está corriendo
kubectl get pods -n security | grep vault

# Acceder a Vault
kubectl port-forward -n security service/vault 8200:8200
```

**Uso**:
```python
# No hacer esto ❌
password = "my_secret_password"

# Usar Vault ✅
# Secretos se inyectan automáticamente vía External Secrets
```

### External Secrets Operator

Sincroniza secretos desde Vault a Kubernetes:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-secret
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: my-secret
    creationPolicy: Owner
  data:
  - secretKey: password
    remoteRef:
      key: secret/data/myapp
      property: password
```

### Airflow Connections

Nunca hardcodear credenciales en código:

```python
# ❌ Malo
hook = PostgresHook(
    postgres_conn_id="db",
    host="localhost",
    login="user",
    password="password"  # ❌ NUNCA
)

# ✅ Bueno
hook = PostgresHook(postgres_conn_id="db")  # Credenciales en Airflow
```

**Crear conexión**:
```bash
airflow connections add db \
  --conn-type postgres \
  --conn-host <host> \
  --conn-login <user> \
  --conn-password <password>
```

---

## 🔑 Autenticación y Autorización

### RBAC en Kubernetes

```yaml
# Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
subjects:
- kind: User
  name: developer
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### OPA Gatekeeper

Políticas de seguridad:

```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          required := input.parameters.labels
          provided := input.review.object.metadata.labels
          missing := required[_]
          not provided[missing]
          msg := sprintf("Missing required label: %v", [missing])
        }
```

### Autenticación en Airflow

```python
# Configurar autenticación OAuth2
[webserver]
auth_backend = airflow.contrib.auth.backends.oauth

# O usar autenticación básica
[webserver]
auth_backend = airflow.contrib.auth.backends.password_auth
```

---

## 🌐 Seguridad de Red

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: airflow
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-postgres
  namespace: airflow
spec:
  podSelector:
    matchLabels:
      app: airflow-worker
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### TLS/SSL

**Certificados**:
```bash
# Usar cert-manager para certificados automáticos
kubectl apply -f security/cert-manager/
```

**Configurar TLS en Ingress**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airflow-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - airflow.example.com
    secretName: airflow-tls
  rules:
  - host: airflow.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: airflow-webserver
            port:
              number: 8080
```

---

## 💾 Seguridad de Datos

### Encryption at Rest

**PostgreSQL**:
```sql
-- Habilitar encryption
CREATE EXTENSION pgcrypto;

-- Encriptar datos sensibles
INSERT INTO users (email, password_hash)
VALUES ('user@example.com', crypt('password', gen_salt('bf')));
```

**Kubernetes Secrets**:
```yaml
# Secrets se encriptan automáticamente en etcd
# Usar encryption providers para encryption adicional
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: <base64-encoded-secret>
```

### Encryption in Transit

**TLS para todas las conexiones**:
- PostgreSQL: Requerir SSL
- API calls: HTTPS solamente
- Inter-service: mTLS donde sea posible

**Configurar PostgreSQL SSL**:
```yaml
# En connection string
postgresql://user:pass@host:5432/db?sslmode=require
```

### Data Masking

```python
def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Enmascara datos sensibles."""
    masked = data.copy()
    
    # Enmascarar emails
    if 'email' in masked:
        email = masked['email']
        masked['email'] = email[0] + '***@' + email.split('@')[1]
    
    # Enmascarar números de tarjeta
    if 'card_number' in masked:
        masked['card_number'] = '****-****-****-' + masked['card_number'][-4:]
    
    return masked
```

---

## 📝 Auditoría y Compliance

### Logging de Auditoría

```python
import logging
from datetime import datetime

audit_logger = logging.getLogger('audit')

def log_access(user: str, resource: str, action: str, success: bool):
    """Registra acceso a recursos."""
    audit_logger.info(
        f"AUDIT: user={user}, resource={resource}, "
        f"action={action}, success={success}, "
        f"timestamp={datetime.utcnow().isoformat()}"
    )
```

### Compliance

**GDPR**:
- Data retention policies
- Right to be forgotten
- Data portability

**SOC 2**:
- Access controls
- Monitoring and alerting
- Incident response

**HIPAA** (si aplica):
- Encryption at rest y in transit
- Access controls
- Audit logs

---

## ✅ Mejores Prácticas

### 1. Nunca Hardcodear Credenciales

```python
# ❌ Malo
password = "secret123"
api_key = "key123456"

# ✅ Bueno
password = os.getenv("DB_PASSWORD")
api_key = os.getenv("API_KEY")
```

### 2. Usar Queries Parametrizadas

```python
# ❌ Vulnerable a SQL injection
sql = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ Seguro
sql = "SELECT * FROM users WHERE id = %s"
hook.get_records(sql, parameters=(user_id,))
```

### 3. Validar Inputs

```python
def process_user_input(user_input: str) -> str:
    """Valida y sanitiza input del usuario."""
    # Validar longitud
    if len(user_input) > 1000:
        raise ValueError("Input too long")
    
    # Sanitizar
    sanitized = user_input.replace("'", "''")  # Escapar SQL
    sanitized = sanitized.replace("<", "&lt;")   # Escapar HTML
    
    return sanitized
```

### 4. Rotar Secretos Regularmente

```bash
# Rotar secretos en Vault
vault kv put secret/myapp password=$(openssl rand -base64 32)

# External Secrets se actualiza automáticamente
```

### 5. Monitorear Accesos

```python
# Registrar todos los accesos a datos sensibles
@task
def access_sensitive_data(**context):
    user = context['dag_run'].conf.get('user')
    log_access(user, 'sensitive_data', 'read', True)
    # Procesar datos
```

---

## ✅ Checklist de Seguridad

### Pre-Deployment

- [ ] Todas las credenciales en Vault/External Secrets
- [ ] Network Policies configuradas
- [ ] RBAC configurado correctamente
- [ ] TLS/SSL configurado
- [ ] Secrets rotados recientemente
- [ ] Inputs validados y sanitizados
- [ ] Queries parametrizadas

### Post-Deployment

- [ ] Monitoreo de accesos activo
- [ ] Alertas de seguridad configuradas
- [ ] Logs de auditoría funcionando
- [ ] Backup de secretos realizado
- [ ] Documentación de seguridad actualizada

### Mantenimiento Continuo

- [ ] Revisar permisos trimestralmente
- [ ] Rotar secretos regularmente
- [ ] Actualizar dependencias de seguridad
- [ ] Revisar logs de auditoría
- [ ] Ejecutar scans de vulnerabilidades

---

## 🚨 Incident Response

### En Caso de Breach

1. **Contener**: Aislar sistemas afectados
2. **Evaluar**: Determinar alcance del breach
3. **Notificar**: Notificar a stakeholders
4. **Remediar**: Corregir vulnerabilidades
5. **Documentar**: Registrar incidente y lecciones aprendidas

### Contactos de Emergencia

- **Security Team**: `#security-incidents` en Slack
- **On-call**: Ver PagerDuty
- **Management**: Según procedimiento de escalación

---

## 📚 Referencias

- [`security/README.md`](../security/README.md) - Documentación de seguridad
- [`docs/TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) - Troubleshooting de seguridad
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Versión**: 1.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

