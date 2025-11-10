# 🚀 Guía de Deployment

> **Versión**: 2.0 | **Última actualización**: 2024 | **Estado**: Producción Ready ✅

Guía completa para desplegar la plataforma en diferentes entornos.

## 📋 Tabla de Contenidos

- [Pre-requisitos](#-pre-requisitos)
- [Preparación](#-preparación)
- [Despliegue en Desarrollo](#-despliegue-en-desarrollo)
- [Despliegue en Staging](#-despliegue-en-staging)
- [Despliegue en Producción](#-despliegue-en-producción)
- [Post-Deployment](#-post-deployment)
- [Rollback](#-rollback)
- [Verificación](#-verificación)
- [Checklist](#-checklist)

---

## 🔧 Pre-requisitos

### Herramientas Requeridas

- **kubectl**: v1.28+
- **helm**: v3.13+
- **terraform**: v1.6+
- **docker**: v24+
- **git**: v2.30+

### Credenciales y Accesos

- Acceso a Kubernetes cluster
- Acceso a Cloud Provider (AWS/Azure/GCP)
- Credenciales de Docker Registry
- Credenciales de base de datos
- Secrets de aplicaciones

### Configuración Inicial

```bash
# Configurar kubectl
aws eks update-kubeconfig --name <cluster-name> --region <region>

# Verificar acceso
kubectl cluster-info
kubectl get nodes

# Configurar Helm
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```

---

## 📦 Preparación

### 1. Clonar Repositorio

```bash
git clone <repository-url>
cd IA
git checkout <branch>
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp environments/dev.yaml.example environments/dev.yaml

# Editar con tus valores
vim environments/dev.yaml
```

### 3. Configurar Secrets

```bash
# Crear namespace
kubectl create namespace <namespace>

# Crear secrets
kubectl create secret generic <secret-name> \
  --from-literal=username=<user> \
  --from-literal=password=<pass> \
  -n <namespace>
```

### 4. Verificar Configuración

```bash
# Validar configuración de Terraform
cd infra/terraform
terraform validate

# Validar manifiestos de Kubernetes
kubectl apply --dry-run=client -f kubernetes/

# Validar Helm charts
helm lint <chart-name>
```

---

## 🛠️ Despliegue en Desarrollo

### Paso 1: Infraestructura Base

```bash
# Inicializar Terraform
cd infra/terraform
terraform init

# Plan
terraform plan -var-file=environments/dev.tfvars

# Aplicar
terraform apply -var-file=environments/dev.tfvars
```

### Paso 2: Kubernetes Base

```bash
# Crear namespaces
kubectl apply -f kubernetes/namespaces.yaml

# Aplicar overlays de desarrollo
kubectl apply -f kubernetes/overlays/dev/

# Verificar
kubectl get namespaces
```

### Paso 3: Componentes Base

```bash
# Desplegar observabilidad
helmfile -f observability/helmfile.yaml apply

# Desplegar seguridad
kubectl apply -f security/secrets/
kubectl apply -f security/policies/

# Verificar
kubectl get pods -n observability
kubectl get pods -n security
```

### Paso 4: Aplicaciones

```bash
# Desplegar Airflow
cd data/airflow
helm upgrade --install airflow apache-airflow/airflow \
  --namespace airflow \
  --values values.yaml \
  --values environments/dev.yaml

# Desplegar Kestra
helm upgrade --install kestra kestra/kestra \
  --namespace workflow \
  --values workflow/kestra/values.yaml

# Verificar
kubectl get pods -n airflow
kubectl get pods -n workflow
```

### Paso 5: Verificación

```bash
# Verificar estado de pods
kubectl get pods -A

# Verificar servicios
kubectl get svc -A

# Verificar ingress
kubectl get ingress -A

# Acceder a aplicaciones
kubectl port-forward -n airflow service/airflow-webserver 8080:8080
```

---

## 🧪 Despliegue en Staging

### Diferencias con Desarrollo

1. **Más recursos**: Aumentar requests/limits
2. **Más réplicas**: Aumentar número de pods
3. **Configuración de producción**: Usar configs similares a prod
4. **Monitoreo completo**: Habilitar todas las alertas

### Proceso

```bash
# 1. Backup de desarrollo (si es necesario)
velero backup create dev-backup-$(date +%Y%m%d)

# 2. Aplicar overlays de staging
kubectl apply -f kubernetes/overlays/stg/

# 3. Actualizar valores
helm upgrade airflow apache-airflow/airflow \
  --namespace airflow \
  --values values.yaml \
  --values environments/stg.yaml

# 4. Verificar
kubectl get pods -n airflow
kubectl get pods -n workflow

# 5. Ejecutar smoke tests
./scripts/smoke-tests.sh
```

### Smoke Tests

```bash
#!/bin/bash
# scripts/smoke-tests.sh

# Verificar que todos los pods están running
kubectl get pods -A | grep -v Running | grep -v Completed

# Verificar que los servicios responden
curl -f http://airflow.staging.example.com/health
curl -f http://kestra.staging.example.com/health

# Verificar que las bases de datos están accesibles
kubectl run -it --rm test --image=postgres:15 --restart=Never -- \
  psql -h <db-host> -U <user> -d <database> -c "SELECT 1"

echo "Smoke tests passed!"
```

---

## 🏭 Despliegue en Producción

### Pre-Deployment

1. **Review de código**: Code review completo
2. **Tests**: Todos los tests pasando
3. **Documentación**: Documentación actualizada
4. **Backup**: Backup completo del sistema actual
5. **Plan de rollback**: Plan de rollback documentado

### Proceso Paso a Paso

#### Paso 1: Preparación

```bash
# Crear branch de release
git checkout -b release/v1.0.0

# Tag de release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Backup completo
velero backup create prod-backup-$(date +%Y%m%d) \
  --include-namespaces airflow,workflow,data
```

#### Paso 2: Infraestructura

```bash
# Planear cambios
cd infra/terraform
terraform plan -var-file=environments/prod.tfvars

# Aplicar (con confirmación)
terraform apply -var-file=environments/prod.tfvars
```

#### Paso 3: Kubernetes

```bash
# Aplicar overlays de producción
kubectl apply -f kubernetes/overlays/prod/

# Verificar cambios
kubectl diff -f kubernetes/overlays/prod/
```

#### Paso 4: Componentes Base

```bash
# Actualizar observabilidad
helmfile -f observability/helmfile.yaml apply

# Actualizar seguridad
kubectl apply -f security/secrets/
kubectl apply -f security/policies/
```

#### Paso 5: Aplicaciones (Canary)

```bash
# Desplegar a subset de pods primero (canary)
helm upgrade airflow apache-airflow/airflow \
  --namespace airflow \
  --values values.yaml \
  --values environments/prod.yaml \
  --set workers.replicas=2  # Reducido inicialmente

# Monitorear
watch kubectl get pods -n airflow

# Si todo OK, escalar a producción completa
helm upgrade airflow apache-airflow/airflow \
  --namespace airflow \
  --values values.yaml \
  --values environments/prod.yaml \
  --set workers.replicas=10  # Producción completa
```

#### Paso 6: Verificación

```bash
# Verificar estado
kubectl get pods -A
kubectl get svc -A
kubectl get ingress -A

# Verificar métricas
# Acceder a Grafana y verificar dashboards

# Ejecutar tests de integración
./scripts/integration-tests.sh
```

---

## ✅ Post-Deployment

### Verificaciones Inmediatas

```bash
# 1. Todos los pods están running
kubectl get pods -A | grep -v Running | grep -v Completed

# 2. Servicios responden
curl -f https://airflow.prod.example.com/health
curl -f https://kestra.prod.example.com/health

# 3. Bases de datos accesibles
# Conectar y ejecutar queries de prueba

# 4. Métricas en Grafana
# Verificar que las métricas están llegando

# 5. Logs sin errores críticos
kubectl logs -n airflow --since=5m | grep -i error
```

### Monitoreo Post-Deployment

- **Primera hora**: Monitoreo intensivo
- **Primeras 24 horas**: Monitoreo continuo
- **Primera semana**: Monitoreo diario

### Comunicación

- Notificar a stakeholders del deployment exitoso
- Documentar cualquier issue encontrado
- Actualizar runbooks si es necesario

---

## ⏪ Rollback

### Rollback de Helm Release

```bash
# Ver historial
helm history airflow -n airflow

# Rollback a versión anterior
helm rollback airflow <revision> -n airflow

# Verificar
kubectl get pods -n airflow
```

### Rollback de Kubernetes

```bash
# Rollback de deployment
kubectl rollout undo deployment/<deployment-name> -n <namespace>

# Ver historial
kubectl rollout history deployment/<deployment-name> -n <namespace>

# Rollback a revisión específica
kubectl rollout undo deployment/<deployment-name> --to-revision=2 -n <namespace>
```

### Rollback de Terraform

```bash
# Ver estado
terraform state list

# Rollback a estado anterior
terraform state pull > state-backup.json
# Restaurar desde backup si es necesario

# O aplicar configuración anterior
git checkout <previous-commit>
terraform apply -var-file=environments/prod.tfvars
```

### Rollback de Base de Datos

```bash
# Restaurar desde backup
velero restore create restore-from-backup \
  --from-backup prod-backup-20240101

# O desde backup de BD
psql -h <host> -U <user> -d <database> < backup.sql
```

---

## 🔍 Verificación

### Health Checks

```bash
# Script de health check
./scripts/health-check.sh

# Verificar endpoints
curl -f https://airflow.prod.example.com/health
curl -f https://kestra.prod.example.com/health
curl -f https://grafana.prod.example.com/api/health
```

### Smoke Tests

```bash
# Ejecutar smoke tests
./scripts/smoke-tests.sh

# Tests de integración
pytest tests/integration/ -v
```

### Performance Tests

```bash
# Verificar performance
# Ejecutar tests de carga si es necesario

# Verificar métricas de performance
# En Grafana, verificar latencia, throughput, etc.
```

---

## 📋 Checklist

### Pre-Deployment

- [ ] Code review completado
- [ ] Tests pasando
- [ ] Documentación actualizada
- [ ] Backup completo realizado
- [ ] Plan de rollback documentado
- [ ] Stakeholders notificados
- [ ] Ventana de mantenimiento acordada

### Deployment

- [ ] Infraestructura desplegada
- [ ] Kubernetes configurado
- [ ] Componentes base desplegados
- [ ] Aplicaciones desplegadas
- [ ] Secrets configurados
- [ ] ConfigMaps aplicados

### Post-Deployment

- [ ] Todos los pods running
- [ ] Servicios respondiendo
- [ ] Health checks pasando
- [ ] Smoke tests pasando
- [ ] Métricas funcionando
- [ ] Logs sin errores críticos
- [ ] Alertas configuradas
- [ ] Documentación actualizada

---

## 🚨 Troubleshooting de Deployment

### Problema: Pods no se crean

**Solución**:
```bash
# Verificar eventos
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Verificar recursos
kubectl describe nodes

# Verificar quotas
kubectl describe quota -n <namespace>
```

### Problema: Image pull errors

**Solución**:
```bash
# Verificar acceso a registry
kubectl run -it --rm test --image=<image> --restart=Never

# Verificar imagePullSecrets
kubectl get secrets -n <namespace> | grep registry
```

### Problema: ConfigMap/Secret no encontrado

**Solución**:
```bash
# Verificar que existe
kubectl get configmap <name> -n <namespace>
kubectl get secret <name> -n <namespace>

# Crear si falta
kubectl create configmap <name> --from-file=<file> -n <namespace>
```

---

## 📚 Recursos Adicionales

- [Kubernetes Deployment Guide](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)
- [Airflow Deployment Guide](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/index.html)

---

**Versión**: 2.0 | **Estado**: Producción Ready ✅  
**Mantenido por**: platform-team  
**Última actualización**: 2024

