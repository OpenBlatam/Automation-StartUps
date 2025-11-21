# Troubleshooting Guide - Terraform

Esta guía cubre problemas comunes y sus soluciones cuando trabajas con Terraform.

## Tabla de Contenidos

1. [Problemas de Inicialización](#problemas-de-inicialización)
2. [Problemas de Backend](#problemas-de-backend)
3. [Problemas de Estado](#problemas-de-estado)
4. [Problemas de Providers](#problemas-de-providers)
5. [Problemas de Autenticación](#problemas-de-autenticación)
6. [Problemas de Aplicación](#problemas-de-aplicación)
7. [Problemas de Validación](#problemas-de-validación)
8. [Problemas Comunes de Recursos](#problemas-comunes-de-recursos)

## Problemas de Inicialización

### Error: `terraform init` falla

**Síntomas:**
```
Error: Failed to install provider
```

**Soluciones:**
1. Verificar conectividad a internet:
   ```bash
   ping registry.terraform.io
   ```

2. Actualizar providers:
   ```bash
   terraform init -upgrade
   ```

3. Limpiar cache y reintentar:
   ```bash
   rm -rf .terraform
   terraform init
   ```

4. Verificar versiones de providers en `providers.tf`

### Error: Provider version conflict

**Síntomas:**
```
Error: Provider version constraints could not be satisfied
```

**Soluciones:**
1. Actualizar versiones en `providers.tf`
2. Usar `terraform init -upgrade`
3. Verificar compatibilidad entre providers

## Problemas de Backend

### Error: Backend configuration not found

**Síntomas:**
```
Error: Backend configuration file not found
```

**Soluciones:**
1. Verificar que el archivo existe:
   ```bash
   ls -la backend-configs/backend-*-*.hcl
   ```

2. Bootstrap backend primero:
   ```bash
   ./scripts/bootstrap-backend-aws.sh dev us-east-1
   ```

3. Usar ruta absoluta si es necesario:
   ```bash
   terraform init -backend-config=$(pwd)/backend-configs/backend-dev-aws.hcl
   ```

### Error: Backend already initialized

**Síntomas:**
```
Error: Backend reinitialization required
```

**Soluciones:**
```bash
# Migrar estado (si cambiaste de backend)
terraform init -migrate-state

# Reconfigurar backend
terraform init -reconfigure
```

### Error: Cannot access S3 bucket

**Síntomas:**
```
Error: Failed to get existing workspaces: AccessDenied
```

**Soluciones:**
1. Verificar credenciales AWS:
   ```bash
   aws sts get-caller-identity
   ```

2. Verificar permisos IAM:
   - `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` en el bucket
   - `dynamodb:GetItem`, `dynamodb:PutItem` en la tabla DynamoDB

3. Verificar que el bucket existe:
   ```bash
   aws s3 ls s3://tf-state-biz-automation
   ```

### Error: DynamoDB table not found

**Síntomas:**
```
Error: ResourceNotFoundException: Requested resource not found
```

**Soluciones:**
1. Crear tabla DynamoDB:
   ```bash
   ./scripts/bootstrap-backend-aws.sh dev us-east-1
   ```

2. Verificar nombre de tabla en configuración:
   ```bash
   aws dynamodb describe-table --table-name tf-state-locks
   ```

## Problemas de Estado

### Error: State locked

**Síntomas:**
```
Error: Error acquiring the state lock
```

**Soluciones:**
1. Verificar si otro proceso está corriendo
2. Esperar a que termine (si es legítimo)
3. Si está bloqueado, desbloquear:
   ```bash
   # Obtener Lock ID del error
   terraform force-unlock <LOCK_ID>
   ```

4. Para AWS, verificar DynamoDB:
   ```bash
   aws dynamodb scan --table-name tf-state-locks
   ```

5. Para Azure, verificar blob leases en Storage Account

### Error: State not found

**Síntomas:**
```
Error: No state file found
```

**Soluciones:**
1. Verificar configuración de backend
2. Verificar que el archivo existe en S3/Azure:
   ```bash
   # AWS
   aws s3 ls s3://tf-state-biz-automation/dev/
   
   # Azure
   az storage blob list --container-name tfstate --account-name sttfstate
   ```

3. Si es nuevo, simplemente inicializa:
   ```bash
   terraform init
   ```

### Error: State mismatch

**Síntomas:**
```
Error: state snapshot was created by Terraform newer than
```

**Soluciones:**
1. Actualizar Terraform:
   ```bash
   terraform version
   # Actualizar si es necesario
   ```

2. Si es necesario, usar versión compatible temporalmente

### Error: Resource not in state

**Síntomas:**
```
Error: Resource does not exist in state
```

**Soluciones:**
1. Importar recurso:
   ```bash
   terraform import aws_s3_bucket.datalake bucket-name
   ```

2. Verificar estado:
   ```bash
   terraform state list
   terraform state show aws_s3_bucket.datalake
   ```

## Problemas de Providers

### Error: Provider authentication failed

**AWS:**
```bash
# Verificar credenciales
aws sts get-caller-identity

# Configurar credenciales
aws configure
# o
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

**Azure:**
```bash
# Verificar login
az account show

# Login si es necesario
az login

# Verificar suscripción
az account list
az account set --subscription "SUBSCRIPTION_ID"
```

### Error: Provider not found

**Síntomas:**
```
Error: Could not find required providers
```

**Soluciones:**
```bash
# Actualizar providers
terraform init -upgrade

# Verificar versions.tf o providers.tf
cat providers.tf
```

## Problemas de Autenticación

### AWS: Invalid credentials

**Soluciones:**
1. Verificar archivo de credenciales:
   ```bash
   cat ~/.aws/credentials
   ```

2. Verificar variables de entorno:
   ```bash
   echo $AWS_ACCESS_KEY_ID
   echo $AWS_SECRET_ACCESS_KEY
   ```

3. Usar perfil específico:
   ```bash
   export AWS_PROFILE=my-profile
   ```

4. Verificar permisos IAM del usuario/rol

### Azure: Not logged in

**Soluciones:**
```bash
# Login interactivo
az login

# Login con Service Principal
az login --service-principal \
  -u $ARM_CLIENT_ID \
  -p $ARM_CLIENT_SECRET \
  --tenant $ARM_TENANT_ID

# Verificar
az account show
```

### Azure: Subscription not found

**Soluciones:**
```bash
# Listar suscripciones
az account list --output table

# Seleccionar suscripción
az account set --subscription "SUBSCRIPTION_ID"
```

## Problemas de Aplicación

### Error: Resource already exists

**Síntomas:**
```
Error: resource already exists
```

**Soluciones:**
1. Importar recurso existente:
   ```bash
   terraform import aws_s3_bucket.datalake bucket-name
   ```

2. O cambiar el nombre del recurso en la configuración

### Error: Timeout waiting for resource

**Síntomas:**
```
Error: timeout waiting for resource
```

**Soluciones:**
1. Aumentar timeout en configuración:
   ```hcl
   resource "aws_instance" "example" {
     timeouts {
       create = "10m"
       update = "10m"
       delete = "10m"
     }
   }
   ```

2. Verificar que el servicio cloud esté disponible

3. Verificar límites de cuota/rate limits

### Error: Dependency violation

**Síntomas:**
```
Error: DependencyViolation: resource cannot be deleted
```

**Soluciones:**
1. Verificar dependencias:
   ```bash
   terraform graph | grep resource_name
   ```

2. Eliminar dependencias primero
3. Usar `terraform destroy -target` para destruir en orden

## Problemas de Validación

### Error: Invalid syntax

**Soluciones:**
1. Validar sintaxis:
   ```bash
   terraform validate
   ```

2. Formatear código:
   ```bash
   terraform fmt -recursive
   ```

3. Verificar errores específicos en output

### Error: Variable not set

**Síntomas:**
```
Error: No value for required variable
```

**Soluciones:**
1. Proporcionar valor:
   ```bash
   terraform apply -var="environment=prod"
   ```

2. Usar archivo tfvars:
   ```bash
   terraform apply -var-file=terraform.tfvars
   ```

3. Usar variables de entorno:
   ```bash
   export TF_VAR_environment=prod
   terraform apply
   ```

### Error: Validation failed

**Soluciones:**
1. Ejecutar validación:
   ```bash
   ./scripts/validate-terraform.sh
   ```

2. Revisar errores específicos
3. Corregir según las sugerencias

## Problemas Comunes de Recursos

### AWS: S3 bucket name already exists

**Solución:**
- Los nombres de S3 deben ser únicos globalmente
- Cambiar nombre o usar un sufijo único

### AWS: VPC CIDR conflict

**Solución:**
- Verificar que el CIDR no se solape con otras VPCs
- Cambiar vpc_cidr en variables

### Azure: Storage account name not available

**Solución:**
- Los nombres deben ser únicos globalmente y seguir reglas específicas
- Usar un nombre diferente o dejar que se auto-genere

### Azure: AKS version not available

**Solución:**
```bash
# Listar versiones disponibles
az aks get-versions --location eastus --output table

# Actualizar kubernetes_version en variables
```

### Kubernetes: Cannot connect to cluster

**Soluciones:**
1. Configurar kubeconfig:
   ```bash
   # AWS
   aws eks update-kubeconfig --name cluster-name --region region
   
   # Azure
   az aks get-credentials --resource-group rg-name --name cluster-name
   ```

2. Verificar credenciales:
   ```bash
   kubectl get nodes
   ```

3. Verificar que el cluster esté en estado "Running"

## Debugging Tips

### Habilitar logs detallados

```bash
export TF_LOG=DEBUG
export TF_LOG_PATH=./terraform.log
terraform apply
```

### Ver plan detallado

```bash
terraform plan -detailed-exitcode -out=tfplan
terraform show tfplan
```

### Verificar configuración

```bash
terraform validate
terraform fmt -check -recursive
```

### Ver estado completo

```bash
terraform state pull > state.json
cat state.json | jq '.'
```

## Obtener Ayuda

1. **Scripts de utilidad:**
   ```bash
   ./scripts/health-check.sh aws dev
   ./scripts/validate-terraform.sh
   ```

2. **Documentación:**
   - `STATE_MANAGEMENT.md` - Gestión de estado
   - `README_STATE.md` - Inicio rápido
   - `scripts/README.md` - Documentación de scripts

3. **Recursos externos:**
   - [Terraform Documentation](https://www.terraform.io/docs)
   - [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws)
   - [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm)

## Checklist de Troubleshooting

Cuando encuentres un error:

- [ ] Ejecutar `terraform validate`
- [ ] Ejecutar `terraform fmt -check`
- [ ] Verificar credenciales de provider
- [ ] Verificar backend configuration
- [ ] Verificar estado: `terraform state list`
- [ ] Ver logs: `TF_LOG=DEBUG terraform apply`
- [ ] Ejecutar health check: `./scripts/health-check.sh`
- [ ] Verificar documentación relevante
- [ ] Revisar outputs de Terraform



