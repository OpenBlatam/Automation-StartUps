# Terraform Examples

Este directorio contiene archivos de ejemplo y templates para configurar Terraform.

## Archivos Disponibles

### `terraform.tfvars.example`

Archivo de ejemplo para variables de Terraform. Copia este archivo y personalízalo para tu entorno.

**Uso:**
```bash
cp examples/terraform.tfvars.example terraform.tfvars
# Edita terraform.tfvars con tus valores
```

**⚠️ Importante:** Nunca commitees `terraform.tfvars` al repositorio ya que puede contener datos sensibles.

## Configuración por Entorno

### Desarrollo (dev)
```hcl
environment = "dev"
kubernetes_version = "1.29"
eks_node_groups = {
  default = {
    min_size = 1
    max_size = 2
    desired_size = 1
    instance_types = ["t3.medium"]
  }
}
```

### Staging (stg)
```hcl
environment = "stg"
kubernetes_version = "1.29"
eks_node_groups = {
  default = {
    min_size = 2
    max_size = 5
    desired_size = 3
    instance_types = ["m5.large"]
  }
}
```

### Producción (prod)
```hcl
environment = "prod"
kubernetes_version = "1.29"
enable_encryption = true
enable_vpc_flow_logs = true
kms_key_id = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID"
eks_node_groups = {
  default = {
    min_size = 3
    max_size = 10
    desired_size = 5
    instance_types = ["m5.xlarge"]
  }
}
```

## Personalización

### Variables Opcionales

- `kms_key_id`: Para cifrado con KMS personalizado (AWS)
- `additional_tags`: Tags adicionales para recursos
- `cluster_name`: Nombre personalizado del cluster
- `kubernetes_version`: Versión específica de Kubernetes

### Variables Requeridas

- `project_name`: Nombre del proyecto
- `environment`: Entorno (dev/stg/prod)
- `aws_region` o `location`: Región de despliegue

## Mejores Prácticas

1. **Usa archivos separados por entorno:**
   ```bash
   terraform.tfvars.dev
   terraform.tfvars.stg
   terraform.tfvars.prod
   ```

2. **Usa variables de entorno para datos sensibles:**
   ```bash
   export TF_VAR_kms_key_id="arn:aws:kms:..."
   terraform apply
   ```

3. **Valida antes de aplicar:**
   ```bash
   terraform validate
   terraform plan
   ```

4. **Documenta valores personalizados:**
   - Mantén un archivo `terraform.tfvars.example` actualizado
   - Documenta cualquier override en el README

## Variables de Entorno Alternativas

En lugar de usar `terraform.tfvars`, puedes usar variables de entorno:

```bash
export TF_VAR_environment=prod
export TF_VAR_project_name=biz-automation
export TF_VAR_aws_region=us-east-1
terraform apply
```

Variables de entorno deben tener el prefijo `TF_VAR_` seguido del nombre de la variable.



