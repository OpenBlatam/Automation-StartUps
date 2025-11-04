# Ingress - Exposición de Servicios

Esta carpeta contiene la configuración del controlador de Ingress (NGINX) para exponer servicios internos de Kubernetes al exterior.

## Descripción

El Ingress Controller actúa como punto de entrada para tráfico HTTP/HTTPS externo, proporcionando:
- **Load Balancing**: Distribución de carga entre servicios
- **TLS Termination**: Terminación SSL/TLS
- **Routing basado en Path/Host**: Enrutamiento a diferentes servicios
- **Autenticación**: Integración con OAuth2-proxy u otros sistemas

## Estructura

```
ingress/
├── nginx-ingress.yaml   # Configuración del Ingress Controller
└── kestra-ingress.yaml  # Ingress para exponer webhooks de Kestra
```

## Componentes

### NGINX Ingress Controller

**Archivo**: `nginx-ingress.yaml`

**Características**:
- LoadBalancer para acceso externo
- Integración con cert-manager para TLS automático
- Rate limiting
- Anotaciones para configuración avanzada

**Instalación**:

El Ingress Controller se instala mediante Helmfile (ver `helmfile.yaml`):

```bash
helmfile apply
```

O manualmente:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  -f kubernetes/ingress/nginx-ingress.yaml
```

## Crear Ingress Resources

### Ejemplo Básico

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kpis-api
  namespace: integration
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - kpis-api.example.com
    secretName: kpis-api-tls
  rules:
  - host: kpis-api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kpis-api
            port:
              number: 80
```

### Ejemplo con Autenticación OAuth2

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airflow-web
  namespace: data
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/auth-url: "https://oauth2-proxy.security.svc.cluster.local/oauth2/auth"
    nginx.ingress.kubernetes.io/auth-signin: "https://oauth2-proxy.security.svc.cluster.local/oauth2/start?rd=$escaped_request_uri"
spec:
  ingressClassName: nginx
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

### Ejemplo con Múltiples Paths

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: platform-services
  namespace: integration
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: platform-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /kpis
        pathType: Prefix
        backend:
          service:
            name: kpis-api
            port:
              number: 80
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: healthz
            port:
              number: 80
      - path: /metrics
        pathType: Prefix
        backend:
          service:
            name: metrics-exporter
      port:
        number: 8080
```

### Kestra Webhooks

**Archivo**: `kestra-ingress.yaml`

Expone los webhooks de Kestra para recibir eventos externos (HubSpot, ManyChat, Stripe, etc.).

```bash
kubectl apply -f kubernetes/ingress/kestra-ingress.yaml
```

**URLs de webhooks**:
- HubSpot → ManyChat: `https://kestra.example.com/api/v1/executions/webhook/workflows/hubspot_to_manychat/hubspot`
- ManyChat → HubSpot: `https://kestra.example.com/api/v1/executions/webhook/workflows/leads_manychats_to_hubspot/manychat`

Ver documentación completa: `workflow/kestra/flows/INTEGRATION_HUBSPOT_MANYCHAT.md`

## Anotaciones Útiles

### TLS y Certificados

```yaml
annotations:
  cert-manager.io/cluster-issuer: letsencrypt-prod
  cert-manager.io/cluster-issuer: letsencrypt-staging  # Para testing
```

### Rate Limiting

```yaml
annotations:
  nginx.ingress.kubernetes.io/rate-limit: "100"  # 100 req/min por IP
  nginx.ingress.kubernetes.io/rate-limit-connections: "10"
  nginx.ingress.kubernetes.io/limit-rps: "10"  # Requests per second
```

### CORS

```yaml
annotations:
  nginx.ingress.kubernetes.io/enable-cors: "true"
  nginx.ingress.kubernetes.io/cors-allow-origin: "https://app.example.com"
  nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
```

### Rewrite

```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /$1
  nginx.ingress.kubernetes.io/use-regex: "true"
```

### SSL Redirect

```yaml
annotations:
  nginx.ingress.kubernetes.io/ssl-redirect: "true"
  nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
```

### WebSockets

```yaml
annotations:
  nginx.ingress.kubernetes.io/websocket-services: "service-name"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
```

## Verificación

### Ver Ingress Resources

```bash
# Ver todos los Ingress
kubectl get ingress -A

# Ver detalles
kubectl describe ingress <name> -n <namespace>

# Ver configuración aplicada
kubectl get ingress <name> -n <namespace> -o yaml
```

### Verificar Certificados

```bash
# Ver certificados
kubectl get certificates -A

# Ver detalles
kubectl describe certificate <name> -n <namespace>

# Ver certificados Let's Encrypt
kubectl get certificaterequests -A
```

### Probar Conectividad

```bash
# Desde fuera del cluster
curl -I https://api.example.com/health

# Desde dentro del cluster
kubectl run -it --rm test --image=curlimages/curl --restart=Never -- \
  curl -I http://ingress-nginx-controller.ingress-nginx.svc.cluster.local \
  -H "Host: api.example.com"
```

## Troubleshooting

### Ingress no funciona

```bash
# Verificar que el Ingress Controller está corriendo
kubectl get pods -n ingress-nginx

# Ver logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Verificar LoadBalancer
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

### Certificado no se crea

```bash
# Verificar ClusterIssuer
kubectl get clusterissuer

# Verificar Certificate
kubectl describe certificate <name> -n <namespace>

# Ver eventos
kubectl get events -n <namespace> --field-selector involvedObject.name=<certificate-name>
```

### Routing incorrecto

```bash
# Ver configuración de NGINX
kubectl exec -n ingress-nginx deployment/ingress-nginx-controller -- \
  cat /etc/nginx/nginx.conf

# Verificar que el servicio existe
kubectl get svc <service-name> -n <namespace>

# Probar endpoint directamente
kubectl port-forward -n <namespace> svc/<service-name> 8080:80
curl http://localhost:8080
```

## Configuración Avanzada

### Custom ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-configuration
  namespace: ingress-nginx
data:
  proxy-buffer-size: "16k"
  proxy-buffers-number: "8"
  client-max-body-size: "10m"
```

Referenciar en `nginx-ingress.yaml`:

```yaml
controller:
  config:
    use-forwarded-headers: "true"
```

## Seguridad

### Network Policies

Asegurar que solo el Ingress Controller puede acceder a servicios:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-only
  namespace: integration
spec:
  podSelector:
    matchLabels:
      app: kpis-api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
```

### WAF (Web Application Firewall)

Considerar usar ModSecurity o similar para protección adicional:

```yaml
annotations:
  nginx.ingress.kubernetes.io/enable-modsecurity: "true"
  nginx.ingress.kubernetes.io/enable-owasp-core-rules: "true"
```

## Referencias

- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Ingress Documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [cert-manager](https://cert-manager.io/)
- [OAuth2-proxy](https://oauth2-proxy.github.io/oauth2-proxy/)

