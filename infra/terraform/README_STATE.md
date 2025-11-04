# Terraform State Management - Quick Start

Este proyecto implementa las mejores prácticas de gestión de estado de Terraform con backends remotos, bloqueo de estado, cifrado y separación por entornos.

## 🚀 Inicio Rápido

### 1. Bootstrap Backend (Primera vez)

**AWS:**
```bash
cd infra/terraform/scripts
./bootstrap-backend-aws.sh dev us-east-1
```

**Azure:**
```bash
cd infra/terraform/scripts
./bootstrap-backend-azure.sh dev eastus
```

### 2. Configurar Backend

Edita el archivo de configuración correspondiente en `backend-configs/`:
- `backend-configs/backend-dev-aws.hcl` para AWS
- `backend-configs/backend-dev-azure.hcl` para Azure

Actualiza los valores necesarios (subscription_id, tenant_id, etc.)

### 3. Inicializar Terraform

```bash
cd infra/terraform
./scripts/init-backend.sh aws dev
# o
./scripts/init-backend.sh azure dev
```

### 4. Usar Terraform Normalmente

```bash
terraform plan
terraform apply
```

## 📁 Estructura de Archivos

```
infra/terraform/
├── backend-aws.tf              # Referencia backend AWS
├── backend-azure.tf            # Referencia backend Azure
├── backend-configs/            # Configuraciones por entorno
│   ├── backend-dev-aws.hcl
│   ├── backend-stg-aws.hcl
│   ├── backend-prod-aws.hcl
│   ├── backend-dev-azure.hcl
│   ├── backend-stg-azure.hcl
│   └── backend-prod-azure.hcl
├── scripts/
│   ├── bootstrap-backend-aws.sh      # Crear recursos backend AWS
│   ├── bootstrap-backend-azure.sh    # Crear recursos backend Azure
│   ├── init-backend.sh                # Inicializar con backend
│   └── state-management.sh            # Utilidades de gestión de estado
└── STATE_MANAGEMENT.md                # Documentación completa
```

## 🔧 Comandos Útiles

### Gestión de Estado

```bash
# Listar recursos
./scripts/state-management.sh list

# Ver detalles de un recurso
./scripts/state-management.sh show aws_s3_bucket.datalake

# Refrescar estado
./scripts/state-management.sh refresh

# Mover recurso en estado
./scripts/state-management.sh mv old_resource new_resource

# Eliminar recurso del estado (no borra el recurso real)
./scripts/state-management.sh rm resource_address
```

### Cambiar de Entorno

```bash
# Desarrollo
terraform init -backend-config=backend-configs/backend-dev-aws.hcl

# Staging
terraform init -backend-config=backend-configs/backend-stg-aws.hcl

# Producción
terraform init -backend-config=backend-configs/backend-prod-aws.hcl
```

## 🔒 Seguridad

- ✅ Estado almacenado en backend remoto (S3/Azure Blob)
- ✅ Cifrado habilitado por defecto
- ✅ Bloqueo de estado con DynamoDB (AWS) o blob lease (Azure)
- ✅ Versionado habilitado para recuperación
- ✅ Estado separado por entorno
- ❌ Nunca commits archivos `.tfstate` al repositorio

## 📚 Documentación Completa

Para más detalles, consulta: [STATE_MANAGEMENT.md](./STATE_MANAGEMENT.md)

## 🆘 Troubleshooting

### Estado Bloqueado

```bash
terraform force-unlock LOCK_ID
```

### Verificar Estado

```bash
terraform state list
terraform plan
```

### Refrescar Estado

```bash
terraform refresh
```

## 🎯 Principios Implementados

1. **Backends Remotos**: S3 (AWS) o Azure Blob Storage
2. **Bloqueo de Estado**: DynamoDB (AWS) o blob leases (Azure)
3. **Cifrado en Reposo**: Habilitado por defecto
4. **Separación por Entornos**: Estados separados para dev/stg/prod
5. **Versionado**: Historial de estados para recuperación
6. **Backups**: Estrategia de respaldo automática



