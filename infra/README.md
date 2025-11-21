# Infraestructura como Código (IaC)

Esta carpeta contiene las definiciones de infraestructura usando Terraform para provisionar recursos en cloud providers (AWS, Azure).

## Estructura

```
infra/
├── terraform/               # Infraestructura como Código
│   ├── main.tf
│   ├── variables.tf
│   └── azure/
├── ansible/                 # Gestión de configuración (Ansible)
│   ├── playbooks/
│   ├── inventory/
│   └── roles/
├── salt/                    # Gestión de configuración (Salt)
│   ├── salt/                # States
│   └── pillar/              # Datos sensibles
├── puppet/                  # Gestión de configuración (Puppet)
│   ├── manifests/
│   ├── modules/
│   └── hiera/
├── chef/                    # Gestión de configuración (Chef)
│   ├── cookbooks/
│   ├── environments/
│   └── roles/
└── jenkins/                 # CI/CD (Jenkins)
    ├── Jenkinsfile
    └── pipelines/
```

## Componentes Provisionados

### Infraestructura Base

1. **VPC/Red Virtual**
   - Subnets públicas y privadas
   - NAT Gateway / Load Balancer
   - Security Groups / Network Security Groups

2. **Kubernetes Cluster**
   - **AWS**: EKS (Elastic Kubernetes Service)
   - **Azure**: AKS (Azure Kubernetes Service)
   - Node groups / Node pools
   - Auto-scaling configurado

3. **Data Lake Storage**
   - **AWS**: S3 bucket con versioning y lifecycle
   - **Azure**: ADLS Gen2 con storage account
   - Configuración de backups

4. **Container Registry** (Azure)
   - ACR (Azure Container Registry) para imágenes Docker

5. **Identidades y Acceso**
   - IAM Roles / Service Principals
   - IRSA (AWS) / Workload Identity (Azure)

## Uso

### Inicialización

```bash
# AWS
cd infra/terraform
terraform init

# Azure
cd infra/terraform/azure
terraform init
```

### Planificación

```bash
# Ver cambios propuestos
terraform plan

# Con variables específicas
terraform plan -var="cluster_name=mi-cluster" -var="region=us-west-2"
```

### Aplicación

```bash
# Aplicar cambios
terraform apply

# Aplicar con confirmación automática (⚠️ usar con cuidado)
terraform apply -auto-approve
```

### Uso con Makefile

El Makefile en la raíz del proyecto proporciona comandos útiles:

```bash
# Inicializar Terraform
make tf-init TF_DIR=infra/terraform

# Validar configuración
make tf-validate TF_DIR=infra/terraform

# Formatear código
make tf-fmt TF_DIR=infra/terraform

# Aplicar cambios
make tf-apply TF_DIR=infra/terraform
```

## Configuración AWS

### Variables Principales

- `cluster_name`: Nombre del cluster EKS
- `aws_region`: Región de AWS
- `vpc_cidr`: CIDR de la VPC
- `private_subnets`: Subnets privadas
- `public_subnets`: Subnets públicas
- `datalake_bucket`: Nombre del bucket S3

### Outputs Importantes

- `cluster_endpoint`: URL del API server de EKS
- `cluster_ca_certificate`: Certificado CA del cluster
- `vpc_id`: ID de la VPC creada
- `s3_bucket_id`: ID del bucket del data lake

### Configurar kubectl

```bash
# Obtener kubeconfig
aws eks update-kubeconfig --name $(terraform output -raw cluster_name) --region $(terraform output -raw aws_region)

# O usar el output de Terraform
terraform output -raw kubeconfig > ~/.kube/config-eks
```

## Configuración Azure

### Variables Principales

- `cluster_name`: Nombre del cluster AKS
- `resource_group`: Grupo de recursos
- `location`: Región de Azure
- `node_count`: Número de nodos inicial
- `vm_size`: Tamaño de las VMs

### Prerrequisitos

1. **Azure CLI** instalado y autenticado:
   ```bash
   az login
   az account set --subscription YOUR_SUBSCRIPTION_ID
   ```

2. **Service Principal** (opcional, para CI/CD):
   ```bash
   az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/YOUR_SUBSCRIPTION_ID"
   ```

### Configurar kubectl

```bash
# Obtener kubeconfig
az aks get-credentials --resource-group $(terraform output -raw resource_group) --name $(terraform output -raw cluster_name)
```

## Estado de Terraform

Este proyecto implementa las mejores prácticas de gestión de estado de Terraform con backends remotos, bloqueo de estado, cifrado y separación por entornos.

### 📚 Documentación Completa

Para información detallada sobre gestión de estado, consulta:
- **[STATE_MANAGEMENT.md](terraform/STATE_MANAGEMENT.md)** - Guía completa de gestión de estado
- **[README_STATE.md](terraform/README_STATE.md)** - Inicio rápido

### 🚀 Inicio Rápido

1. **Bootstrap Backend** (primera vez):
   ```bash
   # AWS
   cd infra/terraform/scripts
   ./bootstrap-backend-aws.sh dev us-east-1
   
   # Azure
   ./bootstrap-backend-azure.sh dev eastus
   ```

2. **Inicializar con Backend**:
   ```bash
   cd infra/terraform
   ./scripts/init-backend.sh aws dev
   # o
   ./scripts/init-backend.sh azure dev
   ```

### Características Implementadas

- ✅ **Backends Remotos**: S3 (AWS) o Azure Blob Storage
- ✅ **Bloqueo de Estado**: DynamoDB (AWS) o blob leases (Azure)
- ✅ **Cifrado en Reposo**: Habilitado por defecto
- ✅ **Separación por Entornos**: Estados separados para dev/stg/prod
- ✅ **Versionado**: Historial de estados para recuperación
- ✅ **Scripts de Utilidad**: Gestión automatizada de estado

### Backend Remoto

**AWS** (S3 + DynamoDB):
- Configuración en `backend-configs/backend-{env}-aws.hcl`
- Requiere S3 bucket con versioning y DynamoDB table para locks
- Ver: `terraform/scripts/bootstrap-backend-aws.sh`

**Azure** (Blob Storage):
- Configuración en `backend-configs/backend-{env}-azure.hcl`
- Requiere Storage Account y Container
- Ver: `terraform/scripts/bootstrap-backend-azure.sh`

### Estado Local

⚠️ **No recomendado para producción**: El estado local puede perderse o causar conflictos.

Para desarrollo local, puedes usar estado local temporalmente, pero migra a backend remoto antes de compartir con el equipo.

## Seguridad

### Buenas Prácticas

1. **Secrets Management**: Nunca hardcodees secrets en `.tf` files
   - Usa variables de entorno: `TF_VAR_db_password`
   - Usa secret stores: AWS Secrets Manager, Azure Key Vault
   - Usa Terraform Cloud/Enterprise para gestión de secrets

2. **IAM Least Privilege**: Roles y políticas mínimas necesarias

3. **Encriptación**: Habilita encriptación en repos (S3/ADLS) y bases de datos

4. **State File**: Protege el estado de Terraform (backend remoto con encriptación)

## Mantenimiento

### Actualizar Módulos

```bash
terraform get -update
terraform init -upgrade
```

### Validación y Linting

```bash
# Validar sintaxis
terraform validate

# Formatear código
terraform fmt -recursive

# Análisis estático (opcional, requiere checkov/tflint)
checkov -d infra/terraform
```

### Destrucción

⚠️ **Cuidado**: Esto eliminará todos los recursos.

```bash
# Plan de destrucción
terraform plan -destroy

# Destruir infraestructura
terraform destroy
```

## Módulos Reutilizables

Considera extraer componentes comunes a módulos:

```
infra/
├── modules/
│   ├── vpc/
│   ├── eks/
│   └── s3/
└── terraform/
    └── main.tf  # Usa los módulos
```

## Integración CI/CD

Ejemplo para GitHub Actions:

```yaml
# .github/workflows/infra.yaml
- name: Terraform Plan
  run: |
    cd infra/terraform
    terraform init
    terraform plan -out=tfplan

- name: Terraform Apply
  if: github.ref == 'refs/heads/main'
  run: terraform apply tfplan
```

## Troubleshooting

### Error: Provider no encontrado

```bash
terraform init -upgrade
```

### Error: Estado bloqueado

```bash
# Verificar locks en backend
# AWS: Revisar DynamoDB table
# Azure: Revisar Storage Account leases
```

### Error: Credenciales

```bash
# AWS
aws configure
# O variables de entorno
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...

# Azure
az login
```

## Herramientas de Gestión de Configuración

Este proyecto integra múltiples herramientas de gestión de configuración para automatizar el setup de servidores después del provisionamiento con Terraform.

### Ansible

Ansible es una herramienta de automatización simple y sin agentes para gestión de configuración.

**Ubicación**: `infra/ansible/`

**Uso**:
```bash
# Instalar dependencias
make ansible-install

# Verificar conectividad
make ansible-ping

# Configurar nodos Kubernetes
make ansible-playbook-k8s

# Configurar servidor Airflow
make ansible-playbook-airflow
```

Ver `infra/ansible/README.md` para más detalles.

### Salt

Salt es un sistema de gestión de configuración basado en estados, optimizado para grandes flotas de servidores.

**Ubicación**: `infra/salt/`

**Uso**:
```bash
# Instalar master
make salt-master-install

# Aplicar estados
make salt-apply

# Aplicar estado específico
make salt-state STATE=k8s.node
```

Ver `infra/salt/README.md` para más detalles.

### Puppet

Puppet utiliza un modelo declarativo para gestionar la configuración de sistemas.

**Ubicación**: `infra/puppet/`

**Uso**:
```bash
# Instalar master
make puppet-master-install

# Aplicar configuración
make puppet-apply
```

Ver `infra/puppet/README.md` para más detalles.

### Chef

Chef utiliza "recipes" y "cookbooks" para gestionar la configuración con un DSL basado en Ruby.

**Ubicación**: `infra/chef/`

**Uso**:
```bash
# Instalar cliente
make chef-client-install

# Subir cookbooks
make chef-upload

# Aplicar configuración
make chef-apply
```

Ver `infra/chef/README.md` para más detalles.

### Jenkins

Jenkins automatiza pipelines completos de CI/CD, integrando todas las herramientas de infraestructura.

**Ubicación**: `infra/jenkins/`

**Uso**:
```bash
# Iniciar Jenkins
make jenkins-up

# Ver logs
make jenkins-logs

# Detener Jenkins
make jenkins-down
```

Ver `infra/jenkins/README.md` para más detalles.

## Flujo de Integración Completo

1. **Terraform**: Provisiona infraestructura (VPC, clusters, storage)
2. **Config Management** (Ansible/Salt/Puppet/Chef): Configura servidores y aplicaciones
3. **Jenkins**: Orquesta el pipeline completo de CI/CD
4. **Kubernetes**: Despliega y gestiona aplicaciones containerizadas

### 🚀 Inicio Rápido

```bash
# Ver todos los comandos disponibles
make help

# Flujo completo automatizado (Terraform + Ansible)
make infra-complete

# Solo Ansible (después de Terraform)
make ansible-complete

# Solo Salt
make salt-complete
```

### 📋 Scripts de Utilidad

- `infra/ansible/examples/quick-start.sh` - Setup rápido interactivo con Ansible
- `infra/scripts/validate-all.sh` - Valida todas las configuraciones

### 📖 Guía Completa de Integración

Ver `INTEGRATION_GUIDE.md` para:
- Comparación de herramientas
- Ejemplos por entorno
- Gestión de secretos
- Troubleshooting
- Integración CI/CD

## 🎯 Comandos Principales del Makefile

### Infraestructura
- `make tf-init` - Inicializar Terraform
- `make tf-plan` - Planificar cambios
- `make tf-apply` - Aplicar cambios
- `make tf-output` - Exportar outputs

### Ansible
- `make ansible-install` - Instalar Ansible
- `make ansible-ping` - Verificar conectividad
- `make ansible-update-inventory` - Actualizar desde Terraform
- `make ansible-playbook-k8s` - Configurar Kubernetes
- `make ansible-playbook-airflow` - Configurar Airflow

### Salt
- `make salt-test` - Test de conectividad
- `make salt-apply` - Aplicar todos los estados
- `make salt-state STATE=k8s.node` - Aplicar estado específico
- `make salt-pillar` - Ver datos de pillar

### Puppet
- `make puppet-apply` - Aplicar configuración
- `make puppet-facts` - Ver facts del sistema
- `make puppet-hiera` - Ver datos de Hiera

### Flujos Completos
- `make infra-complete` - Terraform + Ansible completo
- `make ansible-complete` - Setup completo con Ansible
- `make salt-complete` - Setup completo con Salt

Para ver todos los comandos: `make help`

## 📚 Documentación Adicional

- **Guía de Integración**: Ver `INTEGRATION_GUIDE.md` para flujos completos y comparaciones
- **Ansible**: `infra/ansible/README.md`
- **Salt**: `infra/salt/README.md`
- **Puppet**: `infra/puppet/README.md`

## Referencias

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)
- [Ansible Documentation](https://docs.ansible.com/)
- [Salt Documentation](https://docs.saltproject.io/)
- [Puppet Documentation](https://puppet.com/docs/)
- [Chef Documentation](https://docs.chef.io/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)

