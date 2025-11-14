# 📦 Instalación y Configuración Completa

> Guía detallada para instalar y configurar todos los componentes de la plataforma

## 📋 Tabla de Contenidos

- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación de Herramientas](#-instalación-de-herramientas)
- [Configuración del Entorno](#-configuración-del-entorno)
- [Configuración de Cloud Provider](#-configuración-de-cloud-provider)
- [Despliegue de Infraestructura](#-despliegue-de-infraestructura)
- [Verificación](#-verificación)

## 🖥️ Requisitos del Sistema

### Mínimos
- **CPU**: 4 cores
- **RAM**: 16 GB
- **Disco**: 100 GB libres
- **OS**: Linux, macOS, o WSL2 (Windows)

### Recomendados (Producción)
- **CPU**: 8+ cores
- **RAM**: 32+ GB
- **Disco**: 500+ GB SSD
- **Red**: Conexión estable a internet

## 🛠️ Instalación de Herramientas

### 1. Kubernetes CLI (kubectl)

```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verificar
kubectl version --client
```

### 2. Helm

```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verificar
helm version
```

### 3. Terraform

```bash
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verificar
terraform version
```

### 4. Make

```bash
# macOS (ya viene instalado)
# Linux
sudo apt-get install make  # Debian/Ubuntu
sudo yum install make      # RHEL/CentOS

# Verificar
make --version
```

### 5. Docker (opcional, para desarrollo local)

```bash
# macOS
brew install --cask docker

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verificar
docker --version
```

## ⚙️ Configuración del Entorno

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Cloud Provider
export AWS_REGION=us-east-1
export AWS_PROFILE=default

# O para Azure
export AZURE_SUBSCRIPTION_ID=your-subscription-id
export AZURE_TENANT_ID=your-tenant-id

# Kubernetes
export KUBECONFIG=~/.kube/config
export K8S_NAMESPACE=default

# Dominio (ajusta según tu configuración)
export DOMAIN=your-domain.com
```

### Archivo platform.yaml

Copia y edita el archivo de configuración:

```bash
cp platform.yaml.example platform.yaml
```

Edita `platform.yaml` con tus valores:

```yaml
cloud:
  provider: aws  # aws, azure, gcp
  region: us-east-1
  
kubernetes:
  cluster_name: my-cluster
  namespace: automation-platform
  
ingress:
  domain: your-domain.com
  tls: true
  
components:
  kestra:
    enabled: true
    replicas: 2
  airflow:
    enabled: true
    replicas: 3
  grafana:
    enabled: true
```

## ☁️ Configuración de Cloud Provider

### AWS

```bash
# Configurar credenciales
aws configure

# O usar variables de entorno
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1

# Verificar
aws sts get-caller-identity
```

### Azure

```bash
# Login
az login

# Configurar suscripción
az account set --subscription "your-subscription-id"

# Verificar
az account show
```

### GCP

```bash
# Login
gcloud auth login

# Configurar proyecto
gcloud config set project your-project-id

# Verificar
gcloud config list
```

## 🏗️ Despliegue de Infraestructura

### Paso 1: Inicializar Terraform

```bash
cd infra/terraform
terraform init
```

### Paso 2: Planificar Cambios

```bash
terraform plan -out=tfplan
```

### Paso 3: Aplicar Configuración

```bash
terraform apply tfplan
```

Esto creará:
- Cluster de Kubernetes (si no existe)
- VPC y networking
- Storage buckets
- IAM roles y policies
- Otros recursos necesarios

### Paso 4: Configurar kubectl

```bash
# AWS EKS
aws eks update-kubeconfig --name your-cluster-name --region us-east-1

# Azure AKS
az aks get-credentials --resource-group your-rg --name your-cluster

# GCP GKE
gcloud container clusters get-credentials your-cluster --zone us-central1-a
```

### Paso 5: Verificar Conexión

```bash
kubectl get nodes
```

## 🚀 Despliegue de Componentes

### Usando Make (Recomendado)

```bash
# Desde la raíz del proyecto
make k8s-namespaces
make k8s-ingress
make helmfile-apply
```

### Manualmente con Helmfile

```bash
cd infra/helmfile
helmfile sync
```

### Verificar Despliegue

```bash
# Ver todos los pods
kubectl get pods --all-namespaces

# Ver servicios
kubectl get svc --all-namespaces

# Ver ingress
kubectl get ingress --all-namespaces
```

## ✅ Verificación

### Health Checks

```bash
# Verificar que todos los pods estén Running
kubectl get pods --all-namespaces | grep -v Running

# Verificar logs de errores
kubectl logs -n kestra kestra-server-0 --tail=50

# Verificar métricas
kubectl top nodes
kubectl top pods --all-namespaces
```

### Acceso a Dashboards

Una vez desplegado, accede a:

- **Grafana**: `http://grafana.your-domain.com`
- **Kestra**: `http://kestra.your-domain.com`
- **Airflow**: `http://airflow.your-domain.com`
- **MLflow**: `http://mlflow.your-domain.com`

### Credenciales por Defecto

⚠️ **IMPORTANTE**: Cambia las credenciales por defecto en producción.

Las credenciales iniciales están en:
- `environments/prod.yaml` (para producción)
- `environments/dev.yaml` (para desarrollo)

## 🔧 Configuración Post-Instalación

### 1. Configurar Secretos

```bash
# Usar External Secrets Operator
kubectl apply -f security/external-secrets/

# O configurar manualmente
kubectl create secret generic app-secrets \
  --from-literal=db-password=your-password \
  -n automation-platform
```

### 2. Configurar Storage

```bash
# Verificar que los PVCs estén Bound
kubectl get pvc --all-namespaces

# Si hay problemas, revisa los StorageClasses
kubectl get storageclass
```

### 3. Configurar DNS

Asegúrate de que tus dominios apunten a la IP del Ingress:

```bash
# Obtener IP del Ingress
kubectl get ingress -n ingress-nginx

# Configurar DNS (ejemplo con AWS Route53)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch file://dns-changes.json
```

## 🐛 Troubleshooting

Si encuentras problemas:

1. **Pods en estado Pending**: Revisa recursos disponibles
   ```bash
   kubectl describe pod <pod-name> -n <namespace>
   ```

2. **Pods en CrashLoopBackOff**: Revisa logs
   ```bash
   kubectl logs <pod-name> -n <namespace> --previous
   ```

3. **Problemas de red**: Verifica Network Policies
   ```bash
   kubectl get networkpolicies --all-namespaces
   ```

4. **Más ayuda**: Ve a [Troubleshooting](../04-operacion/troubleshooting.md)

## 📚 Siguientes Pasos

Una vez completada la instalación:

1. [Primeros Pasos](./primeros-pasos.md) - Crea tu primer workflow
2. [Configuración de Entornos](../04-operacion/entornos.md) - Configura Dev/Staging/Prod
3. [Seguridad](../05-seguridad/configuracion.md) - Hardening de seguridad



