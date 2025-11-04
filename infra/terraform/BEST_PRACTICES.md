# Terraform Best Practices

Esta guía recopila las mejores prácticas implementadas en este proyecto y recomendaciones adicionales.

## 📋 Índice

1. [Estructura de Código](#estructura-de-código)
2. [Gestión de Estado](#gestión-de-estado)
3. [Seguridad](#seguridad)
4. [Variables y Configuración](#variables-y-configuración)
5. [Naming y Tagging](#naming-y-tagging)
6. [Versionado](#versionado)
7. [Testing y Validación](#testing-y-validación)
8. [CI/CD](#cicd)
9. [Mantenimiento](#mantenimiento)

## Estructura de Código

### ✅ Organización de Archivos

```
infra/terraform/
├── main.tf              # Recursos principales
├── variables.tf         # Variables de entrada
├── outputs.tf          # Outputs del módulo
├── providers.tf        # Configuración de providers
├── locals.tf           # Valores locales calculados
├── backend-configs/    # Configuraciones de backend
├── examples/           # Ejemplos y templates
└── scripts/            # Scripts de utilidad
```

**Mejores Prácticas:**
- ✅ Separar recursos por función (networking, compute, storage)
- ✅ Usar módulos para componentes reutilizables
- ✅ Mantener archivos pequeños (< 500 líneas)
- ✅ Documentar con comentarios claros

### ✅ Uso de Módulos

```hcl
# ✅ BUENO: Usar módulos oficiales
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.1"
  
  name = local.vpc_name
  cidr = var.vpc_cidr
}

# ❌ EVITAR: Recrear funcionalidad existente
resource "aws_vpc" "main" {
  # ... 100+ líneas de código
}
```

## Gestión de Estado

### ✅ Backend Remoto

**SIEMPRE usar backend remoto:**
```bash
# ✅ CORRECTO
terraform init -backend-config=backend-configs/backend-dev-aws.hcl

# ❌ INCORRECTO (solo para pruebas locales)
# Usar estado local en producción
```

**Características requeridas:**
- ✅ Cifrado habilitado
- ✅ Bloqueo de estado (DynamoDB/Azure Blob Leases)
- ✅ Versionado para recuperación
- ✅ Separación por entorno

### ✅ Estado Separado por Entorno

```hcl
# ✅ CORRECTO: Estados separados
# dev/terraform.tfstate
# stg/terraform.tfstate  
# prod/terraform.tfstate

# ❌ INCORRECTO: Workspace compartido
terraform workspace select dev
terraform workspace select prod  # ¡PELIGROSO!
```

### ✅ Backups Regulares

```bash
# Backup manual
make tf-backup-state PROVIDER=aws ENV=prod

# Backup automático (en CI/CD)
# Agregar a pipeline antes de apply
```

## Seguridad

### ✅ Secrets Management

```hcl
# ✅ CORRECTO: Usar variables sensibles
variable "db_password" {
  type        = string
  sensitive   = true
  description = "Database password"
}

# ❌ INCORRECTO: Hardcodear secrets
resource "aws_db_instance" "db" {
  password = "SuperSecret123!"  # ¡NUNCA!
}
```

**Opciones:**
- Variables de entorno: `TF_VAR_db_password`
- Secrets Manager / Key Vault
- Terraform Cloud/Enterprise

### ✅ Least Privilege

```hcl
# ✅ CORRECTO: Permisos mínimos necesarios
resource "aws_iam_role" "example" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

# Política específica
resource "aws_iam_role_policy" "example" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject"]
      Resource = "arn:aws:s3:::bucket/*"
    }]
  })
}
```

### ✅ Cifrado

```hcl
# ✅ Habilitar cifrado en todos los recursos sensibles
resource "aws_s3_bucket" "datalake" {
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"  # O KMS
      }
    }
  }
}
```

## Variables y Configuración

### ✅ Validación de Variables

```hcl
# ✅ CORRECTO: Validar entradas
variable "environment" {
  type        = string
  description = "Environment name"
  
  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "Environment must be dev, stg, or prod."
  }
}

variable "instance_count" {
  type        = number
  description = "Number of instances"
  
  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "Instance count must be between 1 and 10."
  }
}
```

### ✅ Valores por Defecto Sensatos

```hcl
# ✅ CORRECTO: Defaults apropiados
variable "instance_type" {
  type        = string
  default     = "t3.medium"
  description = "EC2 instance type"
}

variable "enable_monitoring" {
  type        = bool
  default     = true
  description = "Enable CloudWatch monitoring"
}
```

### ✅ Locals para Lógica Compleja

```hcl
# ✅ CORRECTO: Usar locals
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  enable_encryption = var.environment == "prod" || var.enable_encryption
}
```

## Naming y Tagging

### ✅ Convenciones de Nombres

```hcl
# ✅ CORRECTO: Consistente y descriptivo
resource "aws_s3_bucket" "datalake" {
  bucket = "${var.project_name}-${var.environment}-datalake"
}

# ✅ CORRECTO: Usar locals para consistencia
resource "aws_s3_bucket" "datalake" {
  bucket = "${local.name_prefix}-datalake"
}
```

### ✅ Tagging Consistente

```hcl
# ✅ CORRECTO: Tags estándar
locals {
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    },
    var.additional_tags
  )
}

# Aplicar a todos los recursos
resource "aws_instance" "example" {
  tags = local.tags
}
```

## Versionado

### ✅ Pin Provider Versions

```hcl
# ✅ CORRECTO: Versiones específicas
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Permite 5.x pero no 6.x
    }
  }
}
```

### ✅ Terraform Version

```hcl
# ✅ CORRECTO: Versión mínima requerida
terraform {
  required_version = ">= 1.6.0"
}
```

**También usar `.terraform-version`:**
```
1.6.6
```

## Testing y Validación

### ✅ Pre-commit Checks

```bash
# Ejecutar antes de commit
make tf-validate-config
make tf-pre-apply-check ENV=dev
```

### ✅ Validación Continua

```bash
# En CI/CD pipeline
terraform fmt -check
terraform validate
terraform plan
```

### ✅ Health Checks

```bash
# Verificar infraestructura después de cambios
make tf-health-check PROVIDER=aws ENV=dev
make tf-drift-detection PROVIDER=aws ENV=dev
```

## CI/CD

### ✅ Pipeline Estructura

1. **Validate** - Validar sintaxis y formato
2. **Plan** - Mostrar cambios propuestos
3. **Security** - Análisis de seguridad (checkov)
4. **Approval** - Requerir aprobación para producción
5. **Apply** - Aplicar cambios
6. **Verify** - Health checks post-deployment

### ✅ Environment Protection

```yaml
# ✅ CORRECTO: Proteger producción
apply:
  environment:
    name: prod
    # Requiere aprobación manual
```

### ✅ State Locking

```bash
# ✅ Automático con backend remoto
# DynamoDB (AWS) o Blob Leases (Azure)
# Previene aplicaciones concurrentes
```

## Mantenimiento

### ✅ Refrescar Estado Regularmente

```bash
# Detectar cambios manuales
terraform refresh
terraform plan

# Si hay drift, decidir:
# 1. Importar cambios
# 2. Corregir configuración
# 3. Aplicar para sincronizar
```

### ✅ Actualizar Providers

```bash
# Regularmente actualizar providers
terraform init -upgrade

# Probar en dev primero
```

### ✅ Limpiar Recursos Antiguos

```bash
# Limpiar backups antiguos
make tf-cleanup --state

# Limpiar cache
make tf-cleanup --cache
```

### ✅ Documentación

- ✅ Comentar código complejo
- ✅ Mantener README actualizado
- ✅ Documentar decisiones de diseño
- ✅ Incluir ejemplos de uso

## Checklist de Mejores Prácticas

### Antes de Commit
- [ ] `terraform fmt -recursive`
- [ ] `terraform validate`
- [ ] `make tf-validate-config`
- [ ] No hardcodear secrets
- [ ] Revisar cambios con `terraform plan`

### Antes de Apply
- [ ] `make tf-pre-apply-check ENV=dev`
- [ ] Revisar plan completo
- [ ] Verificar entorno correcto
- [ ] Backup de estado (producción)

### Después de Apply
- [ ] `make tf-health-check`
- [ ] Verificar outputs
- [ ] Documentar cambios
- [ ] Notificar equipo si es necesario

## Recursos Adicionales

- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/)

## Herramientas Recomendadas

- **tfenv** - Gestión de versiones de Terraform
- **tflint** - Linter para Terraform
- **checkov** - Análisis de seguridad
- **infracost** - Estimación de costos
- **terragrunt** - DRY para múltiples entornos


