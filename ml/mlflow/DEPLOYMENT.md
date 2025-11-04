# Guía de Deployment de MLflow

Guía completa para desplegar MLflow en diferentes entornos usando Helm.

## 📋 Requisitos Previos

1. **Kubernetes cluster** (EKS, AKS, GKE, o local)
2. **Helm 3.13+** instalado
3. **kubectl** configurado
4. **Namespace** creado:
   ```bash
   kubectl create namespace ml
   ```

5. **External Secrets** configurado (para producción):
   - AWS Secrets Manager o Azure Key Vault
   - External Secrets Operator instalado

6. **PostgreSQL** disponible:
   - Puede ser el incluido en el chart o externo
   - Para producción: PostgreSQL managed (RDS, Azure Database, etc.)

## 🚀 Deployment por Entorno

### Desarrollo

```bash
# 1. Agregar repositorio Helm
helm repo add mlflow https://community-charts.github.io/charts
helm repo update

# 2. Instalar con valores de desarrollo
helm install mlflow mlflow/mlflow \
  --namespace ml \
  --create-namespace \
  -f values.yaml \
  -f values-dev.yaml \
  --set backendStore.postgres.password=mlflow-dev \
  --set artifactStore.s3.bucket=biz-datalake-dev

# 3. Verificar deployment
kubectl get pods -n ml
kubectl get svc -n ml
kubectl get ingress -n ml
```

### Staging

```bash
helm install mlflow mlflow/mlflow \
  --namespace ml-staging \
  --create-namespace \
  -f values.yaml \
  --set backendStore.postgres.passwordFromSecret.enabled=true \
  --set backendStore.postgres.passwordFromSecret.name=mlflow-postgres-secret \
  --set artifactStore.s3.bucket=biz-datalake-staging \
  --set artifactStore.s3.awsIamRole=arn:aws:iam::ACCOUNT:role/mlflow-s3-role \
  --set environment=staging
```

### Producción

```bash
# 1. Crear secrets en External Secrets Manager primero
# Ver: security/secrets/externalsecrets-aws.yaml

# 2. Instalar con valores de producción
helm install mlflow mlflow/mlflow \
  --namespace ml \
  --create-namespace \
  -f values.yaml \
  -f values-prod.yaml \
  --set backendStore.postgres.passwordFromSecret.enabled=true \
  --set backendStore.postgres.passwordFromSecret.name=mlflow-postgres-secret \
  --set artifactStore.s3.awsIamRole=arn:aws:iam::ACCOUNT:role/mlflow-s3-role \
  --set artifactStore.s3.accessKeyFromSecret.enabled=false \
  --set environment=production

# 3. Verificar
kubectl wait --for=condition=available --timeout=300s deployment/mlflow -n ml
```

## 🔧 Configuración Post-Deployment

### 1. Configurar DNS

```bash
# Obtener IP del Ingress
INGRESS_IP=$(kubectl get ingress mlflow -n ml -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Configurar DNS (ejemplo con AWS Route53)
# Ajustar según tu proveedor DNS
```

### 2. Verificar Certificados TLS

```bash
# Verificar certificado
kubectl get certificate -n ml mlflow-tls

# Ver logs de cert-manager si hay problemas
kubectl logs -n cert-manager deployment/cert-manager
```

### 3. Configurar OAuth2-Proxy (Opcional)

Para autenticación en producción:

```bash
# Ver: security/oauth2-proxy/
helm install oauth2-proxy oauth2-proxy/oauth2-proxy \
  --namespace ml \
  -f security/oauth2-proxy/values.yaml
```

### 4. Configurar Network Policies

```bash
# Aplicar Network Policies
kubectl apply -f security/networkpolicies/mlflow-netpol.yaml
```

## 📊 Verificación y Testing

### Health Check

```bash
# Verificar health endpoint
curl https://mlflow.example.com/health

# Esperado: {"status": "ok"}
```

### Test de Conexión

```python
import mlflow

# Configurar tracking URI
mlflow.set_tracking_uri("https://mlflow.example.com")

# Verificar conexión
experiments = mlflow.search_experiments()
print(f"Conectado. Experimentos encontrados: {len(experiments)}")
```

### Test de Escritura

```python
import mlflow

mlflow.set_tracking_uri("https://mlflow.example.com")
mlflow.set_experiment("test-experiment")

with mlflow.start_run():
    mlflow.log_param("test_param", "test_value")
    mlflow.log_metric("test_metric", 1.0)
    print("✅ Escritura exitosa")
```

## 🔄 Actualizaciones

### Upgrade de Versión

```bash
# 1. Backup antes de actualizar
kubectl exec -n ml postgres-pod -- \
  pg_dump -U mlflow mlflow > backup_$(date +%Y%m%d).sql

# 2. Actualizar
helm upgrade mlflow mlflow/mlflow \
  --namespace ml \
  -f values.yaml \
  -f values-prod.yaml \
  --set mlflow.image.tag="2.12.0"

# 3. Verificar
kubectl rollout status deployment/mlflow -n ml
```

### Rollback

```bash
# Ver historial
helm history mlflow -n ml

# Rollback a versión anterior
helm rollback mlflow <revision-number> -n ml
```

## 🔍 Monitoreo Post-Deployment

### Ver Logs

```bash
# Logs de MLflow
kubectl logs -n ml deployment/mlflow -f

# Logs de todos los pods
kubectl logs -n ml -l app=mlflow -f
```

### Verificar Métricas

```bash
# Verificar ServiceMonitor
kubectl get servicemonitor -n ml

# Verificar que Prometheus está scraping
# En Prometheus UI: up{job="mlflow"}
```

### Verificar HPA

```bash
# Ver estado del HPA
kubectl get hpa -n ml mlflow

# Ver detalles
kubectl describe hpa -n ml mlflow
```

## 🛠️ Troubleshooting

### Pod no inicia

```bash
# Ver eventos
kubectl describe pod -n ml -l app=mlflow

# Ver logs de init containers
kubectl logs -n ml <pod-name> -c init-container
```

### Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
kubectl get pods -n ml -l app=postgresql

# Probar conexión
kubectl run -it --rm test-psql --image=postgres:15 \
  --restart=Never -- psql -h postgres.ml.svc.cluster.local -U mlflow -d mlflow
```

### Error de S3

```bash
# Verificar credenciales/IRSA
kubectl describe sa mlflow -n ml

# Verificar permisos
kubectl exec -n ml deployment/mlflow -- \
  aws s3 ls s3://biz-datalake-dev/mlflow/
```

### Ingress no funciona

```bash
# Verificar Ingress
kubectl describe ingress -n ml mlflow

# Verificar cert-manager
kubectl get certificate -n ml
kubectl describe certificate -n ml mlflow-tls
```

## 📚 Comandos Útiles

```bash
# Port-forward para acceso local
kubectl port-forward -n ml service/mlflow 5000:5000

# Escalar manualmente
kubectl scale deployment mlflow -n ml --replicas=5

# Reiniciar deployment
kubectl rollout restart deployment/mlflow -n ml

# Ver recursos utilizados
kubectl top pods -n ml -l app=mlflow

# Ver configuración actual
helm get values mlflow -n ml
```

## 🔐 Checklist de Seguridad (Producción)

- [ ] External Secrets configurado (no passwords hardcodeados)
- [ ] IRSA/Managed Identity configurado para S3
- [ ] TLS habilitado y certificados válidos
- [ ] OAuth2-proxy o autenticación configurada
- [ ] Network Policies aplicadas
- [ ] Security contexts configurados (non-root)
- [ ] Rate limiting habilitado en Ingress
- [ ] Backups automatizados (PostgreSQL + S3)
- [ ] Monitoring y alertas configuradas
- [ ] Logs agregados y accesibles
- [ ] RBAC configurado correctamente

## 📖 Referencias

- Ver `README.md` para documentación completa
- Ver `values.yaml` para todas las opciones configurables
- Scripts útiles en `scripts/`

---

**Última actualización**: 2025-01

