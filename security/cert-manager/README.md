# cert-manager - Gestión Automática de Certificados TLS

Esta carpeta contiene la configuración de cert-manager para la gestión automática de certificados TLS mediante Let's Encrypt y otros proveedores ACME.

## Descripción

cert-manager automatiza la obtención, renovación y gestión de certificados TLS en Kubernetes, eliminando la necesidad de gestionar certificados manualmente.

## Componentes

### ClusterIssuers

**Archivo**: `clusterissuer.yaml`

Define proveedores de certificados (Issuers) a nivel de cluster:

- **letsencrypt-staging**: Para testing (no hay rate limits)
- **letsencrypt-prod**: Para producción

**Aplicar**:

```bash
kubectl apply -f security/cert-manager/clusterissuer.yaml

# Verificar
kubectl get clusterissuer
```

## Instalación de cert-manager

### Con Helmfile

cert-manager está configurado en `helmfile.yaml`:

```bash
helmfile apply
```

### Manualmente

```bash
# Instalar CRDs
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.1/cert-manager.crds.yaml

# Instalar cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

## Uso

### Crear Certificado Automáticamente

Cuando usas un Ingress con la anotación `cert-manager.io/cluster-issuer`, cert-manager crea automáticamente un Certificate:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.example.com
    secretName: my-app-tls  # cert-manager crea este secret automáticamente
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-app
            port:
              number: 80
```

### Crear Certificado Manualmente

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-app-tls
  namespace: default
spec:
  secretName: my-app-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - myapp.example.com
  - www.myapp.example.com
```

**Aplicar**:

```bash
kubectl apply -f my-certificate.yaml
```

## Verificación

### Ver Certificados

```bash
# Ver certificados
kubectl get certificates -A

# Ver detalles
kubectl describe certificate <name> -n <namespace>

# Ver el Secret creado
kubectl get secret <secret-name> -n <namespace>
```

### Ver CertificateRequests

```bash
# Ver solicitudes de certificados
kubectl get certificaterequests -A

# Ver detalles
kubectl describe certificaterequest <name> -n <namespace>
```

### Verificar Estado del Certificado

```bash
# Ver condiciones del certificado
kubectl get certificate <name> -n <namespace> -o jsonpath='{.status.conditions}'

# Verificar que está listo
kubectl get certificate <name> -n <namespace> -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'
```

### Verificar Certificado en el Secret

```bash
# Extraer y verificar certificado
kubectl get secret <secret-name> -n <namespace> -o jsonpath='{.data.tls\.crt}' | \
  base64 -d | openssl x509 -text -noout

# Verificar fecha de expiración
kubectl get secret <secret-name> -n <namespace> -o jsonpath='{.data.tls\.crt}' | \
  base64 -d | openssl x509 -noout -enddate
```

## Configuración Avanzada

### Usar DNS01 Challenge (en lugar de HTTP01)

Para dominios wildcard o cuando HTTP01 no es posible:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod-dns
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ops@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-dns
    solvers:
    - dns01:
        route53:
          region: us-east-1
          # Requiere IAM role con permisos Route53
```

### Configurar Rate Limiting

Let's Encrypt tiene límites de rate:
- **Producción**: 50 certificados por dominio registrado por semana
- **Staging**: Sin límites reales (útil para testing)

**Mejores prácticas**:
- Usar staging para desarrollo/testing
- Usar producción solo cuando esté listo
- Agrupar múltiples hosts en un solo certificado cuando sea posible

### Renovación Automática

cert-manager renueva automáticamente certificados:
- **Antes de expirar**: Renueva cuando quedan < 30 días
- **Reintentos**: Reintenta en caso de fallo
- **Notificaciones**: Puedes configurar alertas (ver monitoreo)

## Troubleshooting

### Certificado no se crea

```bash
# Ver eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp' | \
  grep -i certificate

# Ver logs de cert-manager
kubectl logs -n cert-manager deployment/cert-manager -f

# Verificar ClusterIssuer
kubectl describe clusterissuer letsencrypt-prod

# Verificar que el DNS apunta correctamente
dig myapp.example.com
```

### Error de Rate Limiting

```bash
# Verificar límites alcanzados
kubectl logs -n cert-manager deployment/cert-manager | grep -i "rate limit"

# Solución: Usar staging para testing
# O esperar hasta que expire el rate limit (usualmente 7 días)
```

### CertificateRequest pendiente

```bash
# Ver detalles del CertificateRequest
kubectl describe certificaterequest <name> -n <namespace>

# Posibles causas:
# - DNS no apunta correctamente
# - Firewall bloquea puerto 80 (para HTTP01)
# - Rate limit alcanzado
```

### Error de validación HTTP01

```bash
# Verificar que el Ingress está accesible
curl -I http://myapp.example.com/.well-known/acme-challenge/test

# Verificar que cert-manager puede crear recursos en el namespace
kubectl auth can-i create pods --namespace <namespace> \
  --as=system:serviceaccount:cert-manager:cert-manager
```

## Monitoreo

### Alertas de Expiración

Configurar alertas en Prometheus:

```yaml
# observability/prometheus/alertrules.yaml
groups:
  - name: cert-manager
    rules:
      - alert: CertificateExpiringSoon
        expr: cert_manager_certificate_expiration_timestamp_seconds - time() < 7 * 24 * 3600
        for: 1h
        annotations:
          summary: "Certificate expiring in less than 7 days"
```

### Métricas de Prometheus

cert-manager expone métricas automáticamente:

```bash
# Ver métricas
kubectl port-forward -n cert-manager service/cert-manager 9402:9402
curl http://localhost:9402/metrics

# Métricas clave:
# - cert_manager_certificate_expiration_timestamp_seconds
# - cert_manager_certificate_ready_status
# - cert_manager_acme_client_request_duration_seconds
```

### ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cert-manager
  namespace: cert-manager
spec:
  selector:
    matchLabels:
      app: cert-manager
  endpoints:
    - port: http-metrics
      interval: 30s
```

## Seguridad

### Email del ClusterIssuer

⚠️ **Importante**: Actualizar el email en `clusterissuer.yaml`:

```yaml
spec:
  acme:
    email: ops@your-company.com  # Cambiar este valor
```

Este email recibe notificaciones de expiración de certificados.

### Private Key Storage

Los private keys se almacenan en Secrets de Kubernetes:
- Asegurar que etcd está encriptado
- Considerar usar KMS provider para encriptación adicional
- Rotar keys periódicamente si es necesario

## Mejores Prácticas

1. **Usar staging para desarrollo**: Evita rate limits
2. **Agrupar hosts**: Un certificado para múltiples hosts cuando sea posible
3. **Monitorear expiración**: Configurar alertas 7-14 días antes
4. **DNS01 para wildcards**: Usar DNS01 para certificados `*.example.com`
5. **Backup de private keys**: Considerar backup de Secrets críticos
6. **Validar renovación**: Probar renovación en staging antes de producción

## Referencias

- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [ACME Protocol](https://tools.ietf.org/html/rfc8555)
